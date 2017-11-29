# coding=utf-8
from argparse import ArgumentParser
from sys import stdout, stderr, stdin

from ifj2017.interpreter.interpreter import Interpreter

import logging
logging.getLogger().setLevel(logging.DEBUG)

def main():
    parser = ArgumentParser(
        description='Interpreter for IFJcode17 three address code.',
        epilog="""
        Authors: Josef Kolář (xkolar71, @thejoeejoee), Son Hai Nguyen (xnguye16, @SonyPony), GNU GPL v3, 2017
        """
    )

    parser.add_argument("file", help="path to file of IFJcode17 to interpret")

    # args = parser.parse_args()
    """
    try:
        with open(args.file) as f:
            code = f.read()
    except Exception as e:
        print("Cannot load code from file {} due {}.".format(args.file, e), file=stderr)
        exit(1)
        return
    """
    code= """
    .IFJcode17
DEFVAR GF@%0_&1		#5
GROOT
DEFVAR GF@%0_&2		#5
GROOT
DEFVAR GF@%0_&3		#5
GROOT
DEFVAR GF@%1_a 		#5
GROOT
MOVE GF@%1_a float@0x1.8p+1 #6
GROOT
DEFVAR GF@%1_i		#5
GROOT
MOVE GF@%1_i int@0  #6
GROOT
PUSHS string@gzgfggffg #4
GROOT
PUSHS GF@%1_a       #7
GROOT
FLOAT2R2EINTS
GROOT
PUSHS int@-1
GROOT
ADDS
GROOT
POPS GF@%0_&2
GROOT
POPS GF@%0_&1
GROOT
STRLEN GF@%0_&3 GF@%0_&1
GROOT
LT GF@%0_&3 GF@%0_&2 GF@%0_&3
GROOT
JUMPIFEQ %0_0__asc_zero GF@%0_&3 bool@false
GROOT
GT GF@%0_&3 GF@%0_&2 int@-1
GROOT
JUMPIFEQ %0_0__asc_zero GF@%0_&3 bool@false
GROOT
STRI2INT GF@%0_&3 GF@%0_&1 GF@%0_&2
GROOT
PUSHS GF@%0_&3
GROOT
JUMP %1_0__asc_end
GROOT
LABEL %0_0__asc_zero
GROOT
PUSHS int@0
GROOT
LABEL %1_0__asc_end
GROOT
POPS GF@%1_i
GROOT
WRITE GF@%1_i
GROOT
    """

    Interpreter(
        code,
        state_kwargs=dict(
            stdout=stdout,
            stderr=stderr,
            stdin=stdin
        )
    ).run()

    return 0


if __name__ == '__main__':
    exit(main())
