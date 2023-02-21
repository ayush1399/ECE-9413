INSTRUCTION_SET = dict()

def InstructionWrap(ITYPE, I):
    def WrappedI(*wargs):
        return I(ITYPE, *wargs)
    return WrappedI


# =================
# VECTOR OPERATIONS
# =================


# Vector Operations - VV
def VOVV(VO, self, VR1, VR2, VR3):
    match VO:
        case "ADD":
            pass
        case "SUB":
            pass
        case "MUL":
            pass
        case "DIV":
            pass
    self._update_pc()

INSTRUCTION_SET["ADDVV"] = InstructionWrap("ADD", VOVV)
INSTRUCTION_SET["SUBVV"] = InstructionWrap("SUB", VOVV)
INSTRUCTION_SET["MULVV"] = InstructionWrap("MUL", VOVV)
INSTRUCTION_SET["DIVVV"] = InstructionWrap("DIV", VOVV)


# Vector Operations - VS
def VOVS(VO, self, VR1, VR2, SR1):
    match VO:
        case "ADD":
            pass
        case "SUB":
            pass
        case "MUL":
            pass
        case "DIV":
            pass
    self._update_pc()

INSTRUCTION_SET["ADDVS"] = InstructionWrap("ADD", VOVS)
INSTRUCTION_SET["SUBVS"] = InstructionWrap("SUB", VOVS)
INSTRUCTION_SET["MULVS"] = InstructionWrap("MUL", VOVS)
INSTRUCTION_SET["DIVVS"] = InstructionWrap("DIV", VOVS)


# ===============================
# VECTOR MASK REGISTER OPERATIONS
# ===============================


# Vector Mask Register Operations - VV
def SVMROVV(VMRO, self, VR1, VR2):
    match VMRO:
        case "EQ":
            pass
        case "NE":
            pass
        case "GT":
            pass
        case "LT":
            pass
        case "GE":
            pass
        case "LE":
            pass
    self._update_pc()

INSTRUCTION_SET["SEQVV"] = InstructionWrap("EQ", SVMROVV)
INSTRUCTION_SET["SNEVV"] = InstructionWrap("NE", SVMROVV)
INSTRUCTION_SET["SGTVV"] = InstructionWrap("GT", SVMROVV)
INSTRUCTION_SET["SLTVV"] = InstructionWrap("LT", SVMROVV)
INSTRUCTION_SET["SGEVV"] = InstructionWrap("GE", SVMROVV)
INSTRUCTION_SET["SLEVV"] = InstructionWrap("LE", SVMROVV)

# Vector Mask Register Operations - VS
def SVMROVS(VMRO, self, VR1, SR1):
    match VMRO:
        case "EQ":
            pass
        case "NE":
            pass
        case "GT":
            pass
        case "LT":
            pass
        case "GE":
            pass
        case "LE":
            pass
    self._update_pc()

INSTRUCTION_SET["SEQVS"] = InstructionWrap("EQ", SVMROVS)
INSTRUCTION_SET["SNEVS"] = InstructionWrap("NE", SVMROVS)
INSTRUCTION_SET["SGTVS"] = InstructionWrap("GT", SVMROVS)
INSTRUCTION_SET["SLTVS"] = InstructionWrap("LT", SVMROVS)
INSTRUCTION_SET["SGEVS"] = InstructionWrap("GE", SVMROVS)
INSTRUCTION_SET["SLEVS"] = InstructionWrap("LE", SVMROVS)

# Vector Mask Register Operations - CVM
def CVM(self):
    self._update_pc()
    pass
INSTRUCTION_SET["CVM"] = CVM

# Vector Mask Register Operations - POP
def POP(self, SR1):
    self._update_pc()
    pass
INSTRUCTION_SET["POP"] = POP


# =================================
# VECTOR LENGTH REGISTER OPERATIONS
# =================================


# Vector Length Register Operations - MTCL
def MTCL(self, SR1):
    self._update_pc()
    pass
INSTRUCTION_SET["MTCL"] = MTCL

# Vector Length Register Operations - MFCL
def MFCL(self, SR1):
    self._update_pc()
    pass
INSTRUCTION_SET["MFCL"] = MFCL


# ========================
# MEMORY ACCESS OPERATIONS
# ========================


# Memory Access Operations - 11
def LV(self, VR1, SR1):
    self._update_pc()
    pass
INSTRUCTION_SET["LV"] = LV

# Memory Access Operations - 12
def SV(self, VR1, SR1):
    self._update_pc()
    pass
INSTRUCTION_SET["SV"] = SV

# Memory Access Operations - 13
def LVWS(self, VR1, SR1, SR2):
    self._update_pc()
    pass
INSTRUCTION_SET["LVWS"] = LVWS

# Memory Access Operations - 14
def SVWS(self, VR1, SR1, SR2):
    self._update_pc()
    pass
INSTRUCTION_SET["SVWS"] = SVWS

# Memory Access Operations - 15
def LVI(self, VR1, SR1, VR2):
    self._update_pc()
    pass
INSTRUCTION_SET["LVI"] = LVI

# Memory Access Operations - 16
def SVI(self, VR1, SR1, VR2):
    self._update_pc()
    pass
INSTRUCTION_SET["SVI"] = SVI

# Memory Access Operations - 17
def LS(self, VR1, SR1, Imm):
    self._update_pc()
    pass
INSTRUCTION_SET["LS"] = LS

# Memory Access Operations - 18
def SS(self, VR1, SR1, Imm):
    self._update_pc()
    pass
INSTRUCTION_SET["SS"] = SS


# =================
# SCALAR OPERATIONS
# =================


def SO(SOP, self, SR3, SR1, SR2):
    match SOP:
        case "ADD":
            pass
        case "SUB":
            pass
        case "AND":
            pass
        case "OR":
            pass
        case "XOR":
            pass
        case "SLL":
            pass
        case "SRL":
            pass
        case "SRA":
            pass
    self._update_pc()

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
    match OP:
        case "EQ":
            pass
        case "NE":
            pass
        case "GT":
            pass
        case "LT":
            pass
        case "GE":
            pass
        case "LE":
            pass
    self._update_pc()

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
INSTRUCTION_SET["HALT"] = HALT