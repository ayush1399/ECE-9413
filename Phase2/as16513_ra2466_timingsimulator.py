import os
import argparse

from func_simulator import get_control_flow
from collections import deque

SCALAR_INSTRS = ['ADD', 'SUB', 'AND', 'OR', 'XOR', 'SLL', 'SRL', 'SRA', 'B', 'CVM', 'POP', 'MTCL', 'MFCL']
ADD_INSTRS = ['ADDVV', 'SUBVV', 'ADDVS', 'SUBVS', 'SEQVS', 'SNEVS', 'SGTVS', 'SLTVS', 'SGEVS', 'SLEVS', 'SEQVV', 'SNEVV', 'SGTVV', 'SLTVV', 'SGEVV', 'SLEVV']
DIV_INSTRS = ['DIVVV', 'DIVVS']
MUL_INSTRS = ['MULVV', 'MULVS']

class Config(object):
    def __init__(self, iodir):
        self.filepath = os.path.abspath(os.path.join(iodir, "Config.txt"))
        self.parameters = {} # dictionary of parameter name: value as strings.

        try:
            with open(self.filepath, 'r') as conf:
                self.parameters = {line.split('=')[0].strip(): line.split('=')[1].split('#')[0].strip() for line in conf.readlines() if not (line.startswith('#') or line.strip() == '')}
            print("Config - Parameters loaded from file:  ", self.filepath)
            # print("Config parameters:", self.parameters)
        except:
            print("Config - ERROR: Couldn't open file in path:", self.filepath)
            raise

    def __getattr__(self, key):
        return int(self.parameters[key])

class IMEM(object):
    def __init__(self, iodir):
        self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, "Code.asm"))
        self.instructions = []
        self.resolved_instruction_stream = None
        self.DS = None

    def __getitem__(self, PC):
        if 0 <= PC < len(self.resolved_instruction_stream):
            return self.resolved_instruction_stream[PC]
        else:
            return None

    def resolve_instruction_stream(self):
        self.resolved_instruction_stream, self.DS = get_control_flow(iodir)
        # print(self.resolved_instruction_stream)

    def Read(self, idx): # Use this to read from IMEM.
        if idx < self.size:
            return self.DS[idx]
        # else:
            # print("IMEM - ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)

class DMEM(object):
    # Word addressible - each address contains 32 bits.
    def __init__(self, name, iodir, addressLen, numBanks=0):
        self.name = name
        self.size = pow(2, addressLen)
        self.min_value  = -pow(2, 31)
        self.max_value  = pow(2, 31) - 1
        self.ipfilepath = os.path.abspath(os.path.join(iodir, name + ".txt"))
        self.opfilepath = os.path.abspath(os.path.join(iodir, name + "OP.txt"))
        self.data = []
        self.banks = numBanks
        self.bb = [0 for _ in range(numBanks)]

        try:
            with open(self.ipfilepath, 'r') as ipf:
                self.data = [int(line.strip()) for line in ipf.readlines()]
            # print(self.name, "- Data loaded from file:", self.ipfilepath)
            # print(self.name, "- Data:", self.data)
            self.data.extend([0x0 for i in range(self.size - len(self.data))])
        except:
            # print(self.name, "- ERROR: Couldn't open input file in path:", self.ipfilepath)
            raise

    def Read(self, idx): # Use this to read from DMEM.
        if self.name == "VDMEM":
            bank = idx % self.banks
            if not self.bb[bank]:
                self.bb[bank] = 6
                return True
            else:
                return False
        else:
            return True

    def Write(self, idx): # Use this to write into DMEM.
        if self.name == "VDMEM":
            bank = idx % self.banks
            if not self.bb[bank]:
                self.bb[bank] = 6
                return True
            else:
                return False
        else:
            return True
        
    def cycle(self):
        for i in range(self.banks):
            if self.bb[i]:
                self.bb[i] -= 1

    def remainingCycles(self):
        return max(self.bb)

    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            # print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            # print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)
            raise

class RegisterFile(object):
    def __init__(self, name, count, length = 1, size = 32):
        self.name       = name
        self.reg_count  = count
        self.vec_length = length # Number of 32 bit words in a register.
        self.reg_bits   = size
        self.min_value  = -pow(2, self.reg_bits-1)
        self.max_value  = pow(2, self.reg_bits-1) - 1
        self.registers  = [[0x0 for e in range(self.vec_length)] for r in range(self.reg_count)] # list of lists of integers

    def Read(self, idx):
        pass # Replace this line with your code.

    def Write(self, idx, val):
        pass # Replace this line with your code.

    def dump(self, iodir):
        opfilepath = os.path.abspath(os.path.join(iodir, self.name + ".txt"))
        try:
            with open(opfilepath, 'w') as opf:
                row_format = "{:<13}"*self.vec_length
                lines = [row_format.format(*[str(i) for i in range(self.vec_length)]) + "\n", '-'*(self.vec_length*13) + "\n"]
                lines += [row_format.format(*[str(val) for val in data]) + "\n" for data in self.registers]
                opf.writelines(lines)
            # print(self.name, "- Dumped data into output file in path:", opfilepath)
        except:
            # print(self.name, "- ERROR: Couldn't open output file in path:", opfilepath)
            raise

class FunctionalUnitExecute():
    def __init__(self, instr, PC, dynamicState, config, onCompletion, vdmem):
        self.instr = instr
        self._PC = PC
        self._DS = dynamicState
        self._config = config
        self._flag = False
        self._onCompletion = onCompletion
        self._ocf = False
        self._vdmem = vdmem
        self.numCycles = self.calculateCycles()
        self.lanes = [None for _ in range(config.numLanes)]
        self.conditionalE()
        

    def cycle(self):
        if not self._flag and self.numCycles > 0:
            self.numCycles -= 1
        elif self.instr[0] == "LVWS" or self.instr[0] == "SVWS":
            self.cycle_LVWS_SVWS()
        elif self.instr[0] == "LV" or self.instr[0] == "SV":
            self.cycle_LV_SV()
        elif self.instr[0] == "LVI" or self.instr[0] == "SVI":
            self.cycle_LVI_SVI()

    def conditionalE(self):
        if self.instr[0] == "LVWS" or self.instr[0] == "SVWS":
            self._flag = True
        elif self.instr[0] == "LV" or self.instr[0] == "SV":
            self._flag = True
        elif self.instr[0] == "LVI" or self.instr[0] == "SVI":
            self._flag = True

        if self._flag:
            self.addresses = deque([int(i) for i in self.instr[2][1:-1].split(",")])

    def completed(self):
        if self.numCycles == 0:
            if not self._ocf:
                self._onCompletion["func"](*self._onCompletion["params"])
                self._ocf = True
            return True
        return False
    
    def cycle_LVWS_SVWS(self):
        self.cycle_VLS()

    def cycle_LVI_SVI(self):
        self.cycle_VLS()

    def cycle_LV_SV(self):
        self.cycle_VLS()

    def cycle_VLS(self):
        for i, e in enumerate(self.lanes):
            if e is None and len(self.addresses) > 0:
                self.lanes[i] = self.addresses.popleft()
            if self.lanes[i] is not None:
                r = self._vdmem.Read(self.lanes[i])
                if r:
                    self.lanes[i] = None
        if len(self.addresses) == 0:
            self.numCycles = self._config.vlsPipelineDepth + 6 - 1
            self._flag = False

    def calculateCycles(self):
        if self.instr[0] in SCALAR_INSTRS or self.instr[0] in ['LS', 'SS', 'HALT']:
            return 1
        elif self.instr[0] in ADD_INSTRS or self.instr[0] in MUL_INSTRS or self.instr[0] in DIV_INSTRS:
            VLR = self._DS[self._PC]["VLR"]

            if self.instr[0] in ADD_INSTRS:
                pd = self._config.pipelineDepthAdd
            elif self.instr[0] in MUL_INSTRS:
                pd = self._config.pipelineDepthMul
            elif self.instr[0] in DIV_INSTRS:
                pd = self._config.pipelineDepthDiv

            cyc = (pd - 1 + (VLR / self._config.numLanes))
            return round(cyc) if round(cyc) > cyc else round(cyc) + 1
        else:
            self._flag = True
            return -100

class Core():
    def __init__(self, imem, sdmem, vdmem, config):
        self.IMEM = imem
        self.SDMEM = sdmem
        self.VDMEM = vdmem
        self.config = config

        self.RFs = {"SRF": RegisterFile("SRF", 8),
                    "VRF": RegisterFile("VRF", 8, 64)}
        
        self.PC = 0
        self.cycles = 0
        self.decoded = (None, None)
        self.STALL = False
        self.SRFbb = [False for _ in range(8)]
        self.VRFbb = [False for _ in range(8)]

        self._scalarQueue = deque([])
        self._vectorDataQueue = deque([])
        self._vectorComputeQueue = deque([])

        self._EXFront = {
            "vDQ": None,
            "vCQ": None,
            "sQ": None
        }
        
    def run(self):
        self.IMEM.resolve_instruction_stream()

        while True:
            self.cycles += 1
            
            ret = False
            ret = self.Execute() or ret
            ret = self.InstructionDecode() or ret
            ret = self.InstructionFetch() or ret

            self.VDMEM.cycle()
            if not ret:
                break

    def Execute(self):
        for key in self._EXFront:
            if self._EXFront[key] is None or self._EXFront[key].completed():
                if key == "vDQ" and len(self._vectorDataQueue) > 0:
                    ins = self._vectorDataQueue.popleft()
                    instr, PC, onComplete = ins
                    self._EXFront["vDQ"] = FunctionalUnitExecute(instr, PC, self.IMEM.DS, self.config, onComplete, self.VDMEM)
                elif key == "vCQ" and len(self._vectorComputeQueue) > 0:
                    ins = self._vectorComputeQueue.popleft()
                    instr, PC, onComplete = ins
                    self._EXFront["vCQ"] = FunctionalUnitExecute(instr, PC, self.IMEM.DS, self.config, onComplete, self.VDMEM)
                elif key == "sQ" and len(self._scalarQueue) > 0:
                    ins = self._scalarQueue.popleft()
                    instr, PC, onComplete = ins
                    self._EXFront["sQ"] = FunctionalUnitExecute(instr, PC, self.IMEM.DS, self.config, onComplete, self.VDMEM)
                else:
                    self._EXFront[key] = None
        flag = False
        for key in self._EXFront:
            if self._EXFront[key] is not None and not self._EXFront[key].completed():
                self._EXFront[key].cycle()
                flag = True
            
        return flag

    def InstructionFetch(self):
        if not self.STALL:
            instr = self.IMEM[self.PC]
            self.decoded = (instr, self.PC)
            self.PC += 1
        return (self.IMEM[self.PC] is not None)

    def InstructionDecode(self):
        if not self.decoded[0]:
            return False
        else:
            if self.addToQueue(self.decoded):
                self.STALL = False
            else:
                self.STALL = True
        return True
    
    def addToQueue(self, dcd):
        PC = dcd[1]
        decoded = dcd[0].split(" ")
        d = decoded[0]
        if d == "ADDVV" or d == "SUBVV" or d == "MULVV" or d == "DIVVV" or \
              d == "ADDVS" or d == "SUBVS" or d == "MULVS"  or d == "DIVVS":
            r1, r2, r3 = decoded[1], decoded[2], decoded[3]
            if self.checkRegBB(r1, r2, r3):
                self.updateRegBB(True, r1)

                if len(self._vectorComputeQueue) < self.config.computeQueueDepth:
                    self._vectorComputeQueue.append((decoded, PC, {
                                "func": self.updateRegBB,
                                "params": (False, r1)
                    }))
                    return True
                else:
                    print("DQ")
                    self.updateRegBB(False, r1)

        elif d == "SEQVV" or d == "SNEVV" or d == "SGTVV" or d == "SLTVV" or \
            d == "SGEVV"  or d == "SLEVV" or d == "SEQVS" or d == "SNEVS" or \
            d == "SGTVS" or d == "SLTVS" or d == "SGEVS" or d == "SLEVS":
            r1, r2 = decoded[1], decoded[2]
            if self.checkRegBB(r1, r2):
                self.updateRegBB(True, r1, r2)

                if len(self._vectorComputeQueue) < self.config.computeQueueDepth:
                    self._vectorComputeQueue.append((decoded, PC, {
                    "func": self.updateRegBB,
                    "params": (False, r1)
                }))
                    return True
                else:
                    print("CQ")
                    self.updateRegBB(False, r1, r2)

        elif d == "CVM" or d == "HALT":
            self._scalarQueue.append((decoded, PC, {
                "func": lambda x: x,
                "params": [0] 
            }))
            return True
        
        elif d == "POP" or d == "MTCL" or d == "MFCL":
            r1 = decoded[1]
            if self.checkRegBB(r1):
                self.updateRegBB(True, r1)
                self._scalarQueue.append((decoded, PC, {
                    "func": self.updateRegBB,
                    "params": (False, r1)
                }))
                return True

        elif d == "LS" or d == "SS":
            i = self.IMEM.Read(PC)["I"]
            r1, r2 = i[1], i[2]
            if self.checkRegBB(r1, r2):
                self.updateRegBB(True, r1, r2)
                self._scalarQueue.append((decoded, PC, {
                    "func": self.updateRegBB,
                    "params": (False, r1, r2)
                }))
                return True

        elif d == "ADD" or d == "SUB" or d == "AND" or d == "OR" or \
            d == "XOR" or d == "SLL" or d == "SRL" or d == "SRA":
                r1, r2, r3 = decoded[1], decoded[2], decoded[3]
                if self.checkRegBB(r1, r2, r3):
                    self.updateRegBB(True, r1)
                    self._scalarQueue.append((decoded, PC, {
                    "func": self.updateRegBB,
                    "params": (False, r1)
                }))
                    return True
                
        elif d == "LV" or d == "SV":
            i = self.IMEM.Read(PC)["I"]
            r1, r2 = i[1], i[2]
            if self.checkRegBB(r1, r2):
                self.updateRegBB(True, r1)
                if len(self._vectorDataQueue) < self.config.dataQueueDepth:
                    self._vectorDataQueue.append((decoded, PC, {
                        "func": self.updateRegBB,
                        "params": (False, r1)
                    }))
                else:
                    self.updateRegBB(False, r1)
                return True
            
        elif d == "LVWS" or d == "SVWS" or d == "SVI" or d == "LVI":
            i = self.IMEM.Read(PC)["I"]
            r1, r2, r3 = i[1], i[2], i[3]
            if self.checkRegBB(r1, r2, r3):
                self.updateRegBB(True, r1)
                if len(self._vectorDataQueue) < self.config.dataQueueDepth:
                    self._vectorDataQueue.append((decoded, PC, {
                        "func": self.updateRegBB,
                        "params": (False, r1)
                    }))
                    return True
                else:
                    self.updateRegBB(False, r1)
            
        elif d == "B":
            i = self.IMEM.Read(PC)["I"]
            r1, r2 = i[1], i[2]
            if self.checkRegBB(r1, r2):
                self.updateRegBB(True, r1, r2)
                self._scalarQueue.append((decoded, PC, {
                    "func": self.updateRegBB,
                    "params": (False, r1, r2)
                }))
                return True

        return False
    
    def checkRegBB(self, *args):
        avail = True
        for arg in args:
            r = int(arg[2:])
            if arg[0] == "S":
                avail = avail and not self.SRFbb[r]
            elif arg[0] == "V":
                avail = avail and not self.VRFbb[r]
        return avail

    def updateRegBB(self, val, *args):
         for arg in args:
            r = int(arg[2:])
            if arg[0] == "S":
                self.SRFbb[r] = val
            elif arg[0] == "V":
                self.VRFbb[r] = val

    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Timing Simulator')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse Config
    config = Config(iodir)

    # Parse IMEM
    imem = IMEM(iodir)  
    # Parse SMEM
    sdmem = DMEM("SDMEM", iodir, 13) # 32 KB is 2^15 bytes = 2^13 K 32-bit words.
    # Parse VMEM
    vdmem = DMEM("VDMEM", iodir, 17, config.vdmNumBanks) # 512 KB is 2^19 bytes = 2^17 K 32-bit words. 

    # Create Vector Core
    vcore = Core(imem, sdmem, vdmem, config)

    # Run Core
    vcore.run()

    print(f"\n================================")
    print(f"Total Cycles Taken: {vcore.cycles}".upper())
    print(f"================================\n")

    # THE END