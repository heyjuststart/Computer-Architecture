"""CPU functionality."""

import sys
import re

HLT = 1
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
RET = 0b00010001
CALL = 0b01010000

SP = 7 # index of stack pointer in register

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.running = True
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[RET] = self.handle_ret
        self.branchtable[call] = self.handle_call

    def handle_call(self, a):
        return_addr = pc + 2

        # push return address on stack (same code as push)
        # would need to write a helper though since we want to
        # avoid using a register
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = return_addr
        self.pc = self.reg[a]


    def handle_ret(self):
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    def handle_hlt(self):
        self.running = False
        # self.pc += 1

    def handle_ldi(self, a, b):
        self.reg[a] = b
        # self.pc += 3

    def handle_prn(self, a):
        print(self.reg[a])
        # self.pc += 2

    def handle_mul(self, a, b):
        self.reg[a] = self.reg[a] * self.reg[b]
        # self.pc += 3

    def handle_push(self, a):
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.reg[a]
        # self.pc += 2

    def handle_pop(self, a):
        self.reg[a] = self.ram[self.reg[SP]]
        self.reg[SP] += 1
        # self.pc += 2


    def load(self, filename):
        """Load a program into memory."""

        address = 0
        program = None

        with open(filename) as f:
            program = f.readlines()

        program = [re.sub("#.*$", "", x).strip() for x in program]
        program = [int(x, 2) for x in program if len(x) > 0]

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def run(self):
        """Run the CPU."""
        while self.running:
            self.trace()
            ir = self.ram_read(self.pc)
            num_operands = ir >> 6 # get first 2 bits for operand count
            #                `AABCDDDD`
            sets_pc = (ir & 0b00010000) >> 4 # mask to check C, 1 indicates setting PC
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if ir in self.branchtable:
                if num_operands == 0:
                    self.branchtable[ir]()
                elif num_operands == 1:
                    self.branchtable[ir](operand_a)
                elif num_operands == 2:
                    self.branchtable[ir](operand_a, operand_b)
                if sets_pc is not 1:
                    self.pc += 1 + num_operands
            else:
                if ir is not 0:
                    print(f"Unknown instruction { ir }")
                sys.exit(1)
                self.pc += 1
