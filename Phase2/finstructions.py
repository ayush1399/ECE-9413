import functools

INSTRUCTION_SET = dict()

def InstructionWrap(ITYPE, I) -> int:
    def WrappedI(*wargs):
        return I(ITYPE, *wargs)
    return WrappedI

def int32(x):
    x = x & 0xffffffff
    return (x ^ 0x80000000) - 0x80000000

def lrshift(val, n): return (val << n) & ((1 << 32) - 1)
def rrshift(val, n): return (val % 0x100000000) >> n

# =================
# VECTOR OPERATIONS
# =================


# Vector Operations - VV
def VOVV(VO, self, VR1, VR2, VR3):
    ri = f"{VO}VV {VR1} {VR2} {VR3}"
    VLR = self._VLR
    VMR, VR2, VR3 = self._VMR[:VLR], self._register_read(VR2)[:VLR], self._register_read(VR3)[:VLR]

    match VO:
        case "ADD":
            vr1 = list(map(lambda vr: int32(vr[0] + vr[1]), zip(VR2, VR3)))
        case "SUB":
            vr1 = list(map(lambda vr: int32(vr[0] - vr[1]), zip(VR2, VR3)))
        case "MUL":
            vr1 = list(map(lambda vr: int32(vr[0] * vr[1]), zip(VR2, VR3)))
        case "DIV":
            vr1 = list(map(lambda vr: int32(vr[0] // vr[1]), zip(VR2, VR3)))

    VR1_MASKED = self._register_read(VR1)[:VLR]
    VR1_MASKED = list(map(lambda vr: vr[2] if vr[1] else vr[0], zip(VR1_MASKED, VMR, vr1)))

    self._register_write(VR1, VR1_MASKED)
    self._update_pc()
    return ri

INSTRUCTION_SET["ADDVV"] = InstructionWrap("ADD", VOVV)
INSTRUCTION_SET["SUBVV"] = InstructionWrap("SUB", VOVV)
INSTRUCTION_SET["MULVV"] = InstructionWrap("MUL", VOVV)
INSTRUCTION_SET["DIVVV"] = InstructionWrap("DIV", VOVV)


# Vector Operations - VS
def VOVS(VO, self, VR1, VR2, SR1):
    ri = f"{VO}VS {VR1} {VR2} {SR1}"
    VLR = self._VLR
    VMR, VR2, SR1 = self._VMR[:VLR], self._register_read(VR2)[:VLR], self._register_read(SR1)

    match VO:
        case "ADD":
            vr1 = list(map(lambda vr2_i: int32(vr2_i + SR1), VR2))
        case "SUB":
            vr1 = list(map(lambda vr2_i: int32(vr2_i - SR1), VR2))
        case "MUL":
            vr1 = list(map(lambda vr2_i: int32(vr2_i * SR1), VR2))
        case "DIV":
            vr1 = list(map(lambda vr2_i: int32(vr2_i / SR1), VR2))

    VR1_MASKED = self._register_read(VR1)[:VLR]
    VR1_MASKED = list(map(lambda vr: vr[2] if vr[1] else vr[0], zip(VR1_MASKED, VMR, vr1)))

    self._register_write(VR1, VR1_MASKED)
    self._update_pc()
    return ri

INSTRUCTION_SET["ADDVS"] = InstructionWrap("ADD", VOVS)
INSTRUCTION_SET["SUBVS"] = InstructionWrap("SUB", VOVS)
INSTRUCTION_SET["MULVS"] = InstructionWrap("MUL", VOVS)
INSTRUCTION_SET["DIVVS"] = InstructionWrap("DIV", VOVS)


# ===============================
# VECTOR MASK REGISTER OPERATIONS
# ===============================


# Vector Mask Register Operations - VV
def SVMROVV(VMRO, self, VR1, VR2):
    ri = "S{VMRO}VV {VR1} {VR2}"
    VR1, VR2 = self._register_read(VR1), self._register_read(VR2)
    match VMRO:
        case "EQ":
            self._VMR = list(map(lambda vr_i: 1 if vr_i[0] == vr_i[1] else 0, zip(VR1, VR2)))
        case "NE":
            self._VMR = list(map(lambda vr_i: 1 if vr_i[0] != vr_i[1] else 0, zip(VR1, VR2)))
        case "GT":
            self._VMR = list(map(lambda vr_i: 1 if vr_i[0] > vr_i[1] else 0, zip(VR1, VR2)))
        case "LT":
            self._VMR = list(map(lambda vr_i: 1 if vr_i[0] < vr_i[1] else 0, zip(VR1, VR2)))
        case "GE":
            self._VMR = list(map(lambda vr_i: 1 if vr_i[0] >= vr_i[1] else 0, zip(VR1, VR2)))
        case "LE":
            self._VMR = list(map(lambda vr_i: 1 if vr_i[0] <= vr_i[1] else 0, zip(VR1, VR2)))
    self._update_pc()
    return ri

INSTRUCTION_SET["SEQVV"] = InstructionWrap("EQ", SVMROVV)
INSTRUCTION_SET["SNEVV"] = InstructionWrap("NE", SVMROVV)
INSTRUCTION_SET["SGTVV"] = InstructionWrap("GT", SVMROVV)
INSTRUCTION_SET["SLTVV"] = InstructionWrap("LT", SVMROVV)
INSTRUCTION_SET["SGEVV"] = InstructionWrap("GE", SVMROVV)
INSTRUCTION_SET["SLEVV"] = InstructionWrap("LE", SVMROVV)

# Vector Mask Register Operations - VS
def SVMROVS(VMRO, self, VR1, SR1):
    ri = f"S{VMRO}VS {VR1} {SR1}"
    VR1, SR1 = self._register_read(VR1), self._register_read(SR1)
    match VMRO:
        case "EQ":
            self._VMR = list(map(lambda vr_i: 1 if vr_i == SR1 else 0, VR1))
        case "NE":
            self._VMR = list(map(lambda vr_i: 1 if vr_i != SR1 else 0, VR1))
        case "GT":
            self._VMR = list(map(lambda vr_i: 1 if vr_i > SR1 else 0, VR1))
        case "LT":
            self._VMR = list(map(lambda vr_i: 1 if vr_i < SR1 else 0, VR1))
        case "GE":
            self._VMR = list(map(lambda vr_i: 1 if vr_i >= SR1 else 0, VR1))
        case "LE":
            self._VMR = list(map(lambda vr_i: 1 if vr_i <= SR1 else 0, VR1))
    self._update_pc()
    return ri

INSTRUCTION_SET["SEQVS"] = InstructionWrap("EQ", SVMROVS)
INSTRUCTION_SET["SNEVS"] = InstructionWrap("NE", SVMROVS)
INSTRUCTION_SET["SGTVS"] = InstructionWrap("GT", SVMROVS)
INSTRUCTION_SET["SLTVS"] = InstructionWrap("LT", SVMROVS)
INSTRUCTION_SET["SGEVS"] = InstructionWrap("GE", SVMROVS)
INSTRUCTION_SET["SLEVS"] = InstructionWrap("LE", SVMROVS)

# Vector Mask Register Operations - CVM
def CVM(self):
    self._VMR = [1 for _ in range(64)]
    self._update_pc()
    return "CVM"
INSTRUCTION_SET["CVM"] = CVM

# Vector Mask Register Operations - POP
def POP(self, SR1):
    sum = functools.reduce(lambda acc, val: acc + val, self._VMR)
    self._register_write(SR1, sum)
    self._update_pc()
    return f"POP {SR1}"
INSTRUCTION_SET["POP"] = POP


# =================================
# VECTOR LENGTH REGISTER OPERATIONS
# =================================


# Vector Length Register Operations - MTCL
def MTCL(self, SR1):
    ri = f"MTCL {SR1}"
    self._VLR = self._register_read(SR1)
    self._update_pc()
    return ri
INSTRUCTION_SET["MTCL"] = MTCL

# Vector Length Register Operations - MFCL
def MFCL(self, SR1):
    ri = f"MFCL {SR1}"
    self._register_write(SR1, self._VLR)
    self._update_pc()
    return ri
INSTRUCTION_SET["MFCL"] = MFCL


# ========================
# MEMORY ACCESS OPERATIONS
# ========================


# Memory Access Operations - 11
def LV(self, VR1, SR1):
    VLR, SR1 = self._VLR, self._register_read(SR1)
    vr1 = list(map(lambda idx: self.VDMEM.Read(SR1+idx), range(VLR)))
    VMR = self._VMR[:VLR]

    calced = []
    for idx, ele in enumerate([str(SR1+idx) for idx in range(self._VLR)]):
        if VMR[idx]:
            calced.append(ele)
    ri = f"LV {VR1} ({','.join(calced)})"

    VR1_MASKED = self._register_read(VR1)[:VLR]
    VR1_MASKED = list(map(lambda vr: vr[2] if vr[1] else vr[0], zip(VR1_MASKED, VMR, vr1)))
    self._register_write(VR1, VR1_MASKED)
    self._update_pc()
    return ri
INSTRUCTION_SET["LV"] = LV

# Memory Access Operations - 12
def SV(self, VR1, SR1):
    ri = f"SV {VR1} "
    VLR, SR1, VR1 = self._VLR, self._register_read(SR1), self._register_read(VR1)
    VMR = self._VMR[:VLR]

    calced = []
    for idx, ele in enumerate([SR1+idx for idx in range(self._VLR)]):
        if VMR[idx]:
            calced.append(str(ele))

    ri += f"({','.join(calced)})"

    for idx in range(VLR):
        if VMR[idx]:
            self.VDMEM.Write(SR1+idx, VR1[idx])
    self._update_pc()
    return ri
INSTRUCTION_SET["SV"] = SV

# Memory Access Operations - 13
def LVWS(self, VR1, SR1, SR2):
    ri = f"LVWS {VR1} "
    VLR, SR1, SR2 = self._VLR, self._register_read(SR1), self._register_read(SR2)

    vr1 = list(map(lambda idx: self.VDMEM.Read(SR1+idx), range(0, SR2*VLR, SR2)))
    VMR = self._VMR[:VLR]

    calced = []
    for idx, ele in enumerate([str(SR1+i) for i in range(0, SR2 * self._VLR, SR2)]):
        # if VMR[idx]:
        try:
            if VMR[idx] or not VMR[idx]:
                calced.append(ele)
        except IndexError:
            break
        
    ri += f"({','.join(calced)})"

    VR1_MASKED = self._register_read(VR1)[:VLR]
    VR1_MASKED = list(map(lambda vr: vr[2] if vr[1] else vr[0], zip(VR1_MASKED, VMR, vr1)))
    self._register_write(VR1, VR1_MASKED)
    self._update_pc()
    return ri
INSTRUCTION_SET["LVWS"] = LVWS

# Memory Access Operations - 14
def SVWS(self, VR1, SR1, SR2):
    ri = f"SVWS {VR1} "
    VLR, VR1 =  self._VLR, self._register_read(VR1) 
    SR1, SR2 = self._register_read(SR1), self._register_read(SR2)
    VMR = self._VMR[:VLR]

    calced = []
    for idx, ele in enumerate([SR1+i for i in range(0, SR2 * self._VLR, SR2)]):
        # if VMR[idx]:
        try:
            if VMR[idx] or not VMR[idx]:
                calced.append(str(ele))
        except IndexError:
            break

    ri += f"({','.join(calced)})"

    for idx in range(VLR):
        if (VMR[idx]):
            self.VDMEM.Write(SR1+idx*SR2, VR1[idx])
    self._update_pc()
    return ri
INSTRUCTION_SET["SVWS"] = SVWS

# Memory Access Operations - 15
def LVI(self, VR1, SR1, VR2):
    ri = f"LVI {VR1} "
    VLR, SR1, VR2 = self._VLR, self._register_read(SR1), self._register_read(VR2)
    vr1 = list(map(lambda idx: self.VDMEM.Read(SR1+VR2[idx]), range(VLR)))
    VMR = self._VMR[:VLR]

    calced = []
    for idx, ele in enumerate([str(SR1+i) for i in VR2]):
        # if VMR[idx]:
        try:
            if VMR[idx] or not VMR[idx]:
                calced.append(ele)
        except IndexError:
            break

    ri += f"({','.join(calced)})"

    VR1_MASKED = self._register_read(VR1)[:VLR]
    VR1_MASKED = list(map(lambda vr: vr[2] if vr[1] else vr[0], zip(VR1_MASKED, VMR, vr1)))
    self._register_write(VR1, VR1_MASKED)
    self._update_pc()
    return ri
INSTRUCTION_SET["LVI"] = LVI

# Memory Access Operations - 16
def SVI(self, VR1, SR1, VR2):
    ri = f"SVI {VR1} "
    VLR, VR1, SR1, VR2 = self._VLR, self._register_read(VR1), self._register_read(SR1), self._register_read(VR2)
    VMR = self._VMR[:VLR]

    calced = []
    for idx, ele in enumerate([str(SR1+i) for i in VR2]):
        # if VMR[idx]:
        try:
            if VMR[idx] or not VMR[idx]:
                calced.append(ele)
        except IndexError:
            break

    ri += f"({','.join(calced)})"

    for idx in range(VLR):
        if (VMR[idx]):
            self.VDMEM.Write(SR1+VR2[idx], VR1[idx])
    self._update_pc()
    return ri
INSTRUCTION_SET["SVI"] = SVI

# Memory Access Operations - 17
def LS(self, SR2, SR1, Imm):
    SR1 = self._register_read(SR1)
    ri = f"LS {SR2} ({SR1+int(Imm)})"
    self._register_write(SR2, self.SDMEM.Read(SR1 + int(Imm)))
    self._update_pc()
    return ri
INSTRUCTION_SET["LS"] = LS

# Memory Access Operations - 18
def SS(self, SR2, SR1, Imm):
    SR1, SR2 = self._register_read(SR1), self._register_read(SR2)
    ri = f"SS {SR2} ({SR1+int(Imm)})"
    self.SDMEM.Write(SR1+int(Imm), SR2)
    self._update_pc()
    return ri
INSTRUCTION_SET["SS"] = SS


# =================
# SCALAR OPERATIONS
# =================


def SO(SOP, self, SR3, SR1, SR2):
    ri = f"{SOP} {SR3} {SR1} {SR2}"
    SR1, SR2 = self._register_read(SR1), self._register_read(SR2)
    match SOP:
        case "ADD":
            sr3 = int32(SR1 + SR2)
        case "SUB":
            sr3 = int32(SR1 - SR2)
        case "AND":
            sr3 = int32(SR1 & SR2)
        case "OR":
            sr3 = int32(SR1 | SR2)
        case "XOR":
            sr3 = int32(SR1 ^ SR2)
        case "SLL":
            sr3 = lrshift(SR1, SR2)
        case "SRL":
            sr3 = rrshift(SR1, SR2)
        case "SRA":
            sr3 = int32(SR1 >> SR2)
    self._register_write(SR3, sr3)
    self._update_pc()
    return ri

INSTRUCTION_SET["ADD"] = InstructionWrap("ADD", SO)
INSTRUCTION_SET["SUB"] = InstructionWrap("SUB", SO)
INSTRUCTION_SET["AND"] = InstructionWrap("AND", SO)
INSTRUCTION_SET["OR"] = InstructionWrap("OR", SO)
INSTRUCTION_SET["XOR"] = InstructionWrap("XOR", SO)
INSTRUCTION_SET["SLL"] = InstructionWrap("SLL", SO)
INSTRUCTION_SET["SRL"] = InstructionWrap("SRL", SO)
INSTRUCTION_SET["SRA"] = InstructionWrap("SRA", SO)


# =======
# CONTROL
# =======


def B(OP, self, SR1, SR2, Imm):
    SR1, SR2 = self._register_read(SR1), self._register_read(SR2)
    flag = False
    match OP:
        case "EQ":
            flag = (SR1 == SR2)
        case "NE":
            flag = (SR1 != SR2)
        case "GT":
            flag = (SR1 > SR2)
        case "LT":
            flag = (SR1 < SR2)
        case "GE":
            flag = (SR1 >= SR2)
        case "LE":
            flag = (SR1 <= SR2)
    if flag:
        return f"B ({self._update_pc(int(Imm))})"
    else:
        return f"B ({self._update_pc()})"

INSTRUCTION_SET["BEQ"] = InstructionWrap("EQ", B)
INSTRUCTION_SET["BNE"] = InstructionWrap("NE", B)
INSTRUCTION_SET["BGT"] = InstructionWrap("GT", B)
INSTRUCTION_SET["BLT"] = InstructionWrap("LT", B)
INSTRUCTION_SET["BGE"] = InstructionWrap("GE", B)
INSTRUCTION_SET["BLE"] = InstructionWrap("LE", B)


# ====
# HALT
# ====

# Halt - 24
def HALT(self):
    self._update_pc(None, True)
    return "HALT"
INSTRUCTION_SET["HALT"] = HALT