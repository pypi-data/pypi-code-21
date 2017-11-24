import sys
import traceback
import os

def dprint(s):
    if os.getenv('DEBUG'):
        print("\033[35mDPRINT\033[0m: %s" % s)


def dstack():
    if os.getenv('DEBUG'):
        stack = []
        _, _, exc_tb = sys.exc_info()

        if exc_tb:
            for filename, linenum, funcname, source in traceback.extract_tb(exc_tb):
                stack.append("\033[35mTRACEINFO\033[0m: %-23s:%s '%s' in %s()" % (filename, linenum, source, funcname))

        print('\n'.join(stack))