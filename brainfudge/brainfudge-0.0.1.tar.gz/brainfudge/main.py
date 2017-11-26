from enum import Enum

TAPE = {0:0}
POINTER = 0

def debug():
    print('')
    print(TAPE)
    print(POINTER)

def add():
    TAPE[POINTER] += 1

def sub():
    TAPE[POINTER] -= 1

def left():
    global POINTER
    POINTER -= 1
    if not POINTER in TAPE:
        TAPE[POINTER] = 0

def right():
    global POINTER
    POINTER += 1
    if not POINTER in TAPE:
        TAPE[POINTER] = 0

def p():
    print(chr(TAPE[POINTER]), end='')

def inp():
    TAPE[POINTER] = ord(input())

class Parser:

    def __init__(self, tokens):
        self.lex = tokens
        self.tape = {0:0}
        self.code = []

    def duplicate(self, method):
        if not len(self.code):
            self.code.append([1, method])
        if self.code[len(self.code)-1][1] == method:
            self.code[len(self.code)-1][0] += 1
        else:
            self.code.append([1, method])


    def parse(self):
        for token in self.lex:
            if token == '+':
                token = add
                self.duplicate(token)
            elif token == '-':
                token = sub
                self.duplicate(token)
            elif token == '>':
                token = right
                self.duplicate(token)
            elif token == '<':
                token = left
                self.duplicate(token)
            elif token == '.':
                token = p
                self.duplicate(token)
            elif token == ',':
                token = inp
                self.duplicate(token)
            elif token == '?':
                token = debug
                self.duplicate(token)
            else:
                self.code.append([0, token])

def execute(code):
    starts = []
    for i, cmd in enumerate(code):
        if cmd[1] == '[':
            starts.append((i, POINTER))
        elif cmd[1] == ']':
            if len(starts) == 1:
                while TAPE[POINTER] > 1:
                    execute(code[starts[0][0]:i])
            else:
                starts.pop()
        else:
            for _ in range(cmd[0]):
                cmd[1]()

def run(code):
    p = Parser(code)
    p.parse()
    execute((p.code))