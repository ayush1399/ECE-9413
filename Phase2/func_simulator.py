import os
import argparse

from finstructions import INSTRUCTION_SET

class IMEM(object):
    def __init__(self, iodir):
        self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, "Code.asm"))
        self.instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                # self.instructions = [ins.strip() for ins in insf.readlines()]
                self.instructions = [ins.split('#')[0].strip() for ins in insf.readlines() if not (ins.startswith('#') or ins.strip() == '')]
            print(f"IMEM   - Instructions loaded from file: {self.filepath}")
            # print("IMEM - Instructions:", self.instructions)
        except:
            print(f"IMEM - ERROR: Couldn't open file in path:{self.filepath}")

    def Read(self, idx): # Use this to read from IMEM.
        if idx < self.size:
            return self.instructions[idx]
        else:
            print(f"IMEM - ERROR: Invalid memory access at index: {idx} with memory size: {self.size}")

class DMEM(object):
    # Word addressible - each address contains 32 bits.
    def __init__(self, name, iodir, addressLen):
        self.name = name
        self.size = pow(2, addressLen)
        self.min_value  = -pow(2, 31)
        self.max_value  = pow(2, 31) - 1
        self.ipfilepath = os.path.abspath(os.path.join(iodir, name + ".txt"))
        self.opfilepath = os.path.abspath(os.path.join(iodir, name + "OP.txt"))
        self.data = []

        try:
            with open(self.ipfilepath, 'r') as ipf:
                self.data = [int(line.strip()) for line in ipf.readlines()]
                
            print(f"{self.name} - Data loaded from file:          {self.ipfilepath}")
            # print(self.name, "- Data:", self.data)
            self.data.extend([0x0 for i in range(self.size - len(self.data))])
        except:
            print(f"{self.name}- ERROR: Couldn't open input file in path:{self.ipfilepath}")

    def Read(self, idx): # Use this to read from DMEM.
        if 0 <= idx < self.size:
            return self.data[idx]
        else:
            raise Exception(f"DMEM - ERROR: Invalid memory access at index: {idx} with memory size: {self.size}")

    def Write(self, idx, val): # Use this to write into DMEM.
        if 0 <= idx < self.size:
            self.data[idx] = val
        else:
            raise Exception(f"DMEM - ERROR: Invalid memory access at index: {idx} with memory size: {self.size}")

    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)

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
        try:
            return self.registers[idx]
        except IndexError:
            raise Exception("Invalid register read.")

    def Write(self, idx, val):
        # print(f"Write -  idx: {idx}   val: {val}")
        try:
            register = self.registers[idx]
            for i, v in enumerate(val):
                register[i] = v
        except IndexError:
            raise Exception("Invalid register write.")

    def dump(self, iodir):
        opfilepath = os.path.abspath(os.path.join(iodir, self.name + ".txt"))
        try:
            with open(opfilepath, 'w') as opf:
                row_format = "{:<13}"*self.vec_length
                lines = [row_format.format(*[str(i) for i in range(self.vec_length)]) + "\n", '-'*(self.vec_length*13) + "\n"]
                lines += [row_format.format(*[str(val) for val in data]) + "\n" for data in self.registers]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", opfilepath)

class Core():
    def __init__(self, imem, sdmem, vdmem):
        self.IMEM = imem
        self.SDMEM = sdmem
        self.VDMEM = vdmem

        self.RFs = {"SRF": RegisterFile("SRF", 8),
                    "VRF": RegisterFile("VRF", 8, 64)}
        
        self._VMR = [1 for _ in range(64)]
        self._VLR = 64

        self.__ISET = INSTRUCTION_SET
        self._pc = 0
        
    def run(self):
        resolved_flow = []
        dynamicState = []
        try:
            for INS, OPR in self.__exec:

                if OPR:
                    resolved_flow.append(self[INS](self, *OPR))
                    dynamicState.append({
                        "I": [INS] + OPR,
                        "PC": self._pc,
                        "VMR": self._VMR,
                        "VLR": self._VLR
                    })
                else:
                    resolved_flow.append(self[INS](self))
                    dynamicState.append({
                        "I": [INS],
                        "PC": self._pc,
                        "VMR": self._VMR,
                        "VLR": self._VLR
                    })
        except ValueError as err:
            print(INS, OPR)
            return resolved_flow
        return resolved_flow, dynamicState

    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

    def _update_pc(self, i=1, _set=False):
        if _set:
            self._pc = i
        else:
            self._pc += i
        return self._pc

    def _register_read(self, R):
        if R[0] == "S":
            return self.RFs["SRF"].Read(int(R[2:]))[0]
        elif R[0] == "V":
            return self.RFs["VRF"].Read(int(R[2:]))

    def _register_write(self, R, val):
        if R[0] == "S":
            self.RFs["SRF"].Write(int(R[2:]), [val])
        elif R[0] == "V":
            self.RFs["VRF"].Write(int(R[2:]), val)

    @property
    def __exec(self):
        while self._pc is not None:
            ins = self.IMEM.Read(self._pc).split(" ")
            opr = ins[1:] if len(ins) > 1 else None
            yield (ins[0], opr)

    def __getitem__(self, name):
        try:
            return self.__ISET[name]
        except KeyError:
            print("Invalid instruction (core dumped)", name)

def get_control_flow(iodir):
    imem = IMEM(iodir)
    sdmem = DMEM("SDMEM", iodir, 13)
    vdmem = DMEM("VDMEM", iodir, 17)
    vcore = Core(imem, sdmem, vdmem)
    r = vcore.run()
    vcore.dumpregs(iodir)
    sdmem.dump()
    vdmem.dump()
    return r

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Performance Model')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse IMEM
    imem = IMEM(iodir)  
    # Parse SMEM
    sdmem = DMEM("SDMEM", iodir, 13) # 32 KB is 2^15 bytes = 2^13 K 32-bit words.
    # Parse VMEM
    vdmem = DMEM("VDMEM", iodir, 17) # 512 KB is 2^19 bytes = 2^17 K 32-bit words. 

    # Create Vector Core
    vcore = Core(imem, sdmem, vdmem)

    # Run Core
    vcore.run()   
    vcore.dumpregs(iodir)

    sdmem.dump()
    vdmem.dump()

    # THE END