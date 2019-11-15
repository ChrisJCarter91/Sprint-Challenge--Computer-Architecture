"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        # Program Counter
        self.pc = 0  
        self.operations = {
            "LDI": 0b10000010,
            "HLT": 0b00000001,
            "PRN": 0b01000111,
            "ADD": 0b10100000,
            "MUL": 0b10100010,
            "PUSH": 0b01000101,
            "POP": 0b01000110,
            "NOP": 0b00000000,
            "CMP": 0b10100111,
            "JMP": 0b01010100,
            "JEQ": 0b01010101,
            "JNE": 0b01010110, 
        }
        self.sp = 0xF4
        self.flag = 0b00000000

        '''
        Register map:
        +-----------------------+
        | R0                     |
        | R1                     |
        | R2                     |
        | R3                     |
        | R4                     |
        | R5 Interrupt Mask      |
        | R6 Interrupt Status    |
        | R7 Stack Pointer       |
        +-----------------------+

        Memory map:
        Top of RAM
        +-----------------------+
        | FF  I7 vector         |    Interrupt vector table
        | FE  I6 vector         |
        | FD  I5 vector         |
        | FC  I4 vector         |
        | FB  I3 vector         |
        | FA  I2 vector         |
        | F9  I1 vector         |
        | F8  I0 vector         |
        | F7  Reserved          |
        | F6  Reserved          |
        | F5  Reserved          |
        | F4  Key pressed       |    Holds the most recent key pressed on the keyboard
        | F3  Start of Stack    |
        | F2  [more stack]      |    Stack grows down
        | ...                   |
        | 01  [more program]    |
        | 00  Program entry     |    Program loaded upward in memory starting at 0
        +-----------------------+
    Bottom of RAM

        '''

    def ram_read(self, MAR):
        return self.ram[MAR]
        

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR


    def load(self):
#        """Load a program into memory."""

            address = 0

            if len(sys.argv) != 2:
                print("usage: ls8.py filename")
                sys.exit(1)

            with open(sys.argv[1]) as f:
                for line in f:

                    line = line.split("#")[0]
                    line = line.strip()

                    if line == "":
                        continue
                    val = int(line, 2)
                    self.ram[address] = val
                    address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == self.operations["MUL"]:
           self.reg[reg_a] *= self.reg[reg_b]

        elif op == self.operations["CMP"]:
            #FL bits: 00000LGE 
            x_1 = self.reg[reg_a]
            x_2 = self.reg[reg_b]
            #If equal, set to 1, otherwise set to 0
            if x_1 == x_2:
                self.flag = 0b00000001
            #if reg a is less than reg b, set the less than flag to 1, otherwise 0
            if x_1 < x_2:
                self.flag = 0b00000100
            #if reg a is greater than g flag to 1 otherwise 0
            if x_1 > x_2:
                self.flag = 0b00000010

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        halted = False
        
        while not halted:
            IR = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR == self.operations["LDI"]:
                self.reg[operand_a] = operand_b
                self.pc += 3
                
            elif IR == self.operations["PRN"]:
                if IR == self.operations["NOP"]:
                    self.pc += 1
                value = int(self.reg[operand_a])
                print(f"{value}")
                self.pc += 2

            elif IR == self.operations["HLT"]:
                halted = True

            elif IR == self.operations["MUL"]:
                self.alu(self.operations["MUL"], operand_a, operand_b)
                self.pc += 3

            elif IR == self.operations["PUSH"]:
                self.sp = (self.sp-1) & 0xFF
                self.ram[self.sp] = self.reg[operand_a]
                self.pc += 2

            elif IR == self.operations["POP"]:
                self.reg[operand_a] = self.ram[self.sp]
                self.sp = (self.sp + 1) & 0xFF
                self.pc += 2

            elif IR == self.operations["CMP"]:
                self.alu(self.operations["CMP"], operand_a, operand_b)
                self.pc += 3

            elif IR == self.operations["JMP"]:
                self.pc = self.reg[operand_a]

            elif IR == self.operations["JEQ"]:
                if self.flag == 0b00000001:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            elif IR == self.operations["JNE"]:
                if self.flag & 0b00000001 == 0b00000000:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            else:
                print(f"Unknown instruction at index {self.pc}")
                self.pc += 1
