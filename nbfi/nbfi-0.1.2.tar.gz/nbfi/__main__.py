'''Brainfuck interpreter command line main'''

import nbfi

if __name__ == '__main__':
    print("New Brainfuck interpreter %s" % nbfi.VERSION)
    nbfi.run(stack_size=512)
