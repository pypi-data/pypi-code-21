'''Brainfuck interpreter command line main'''

import nbfi

if __name__ == '__main__':
    nbfi.run(stack_size=512)
