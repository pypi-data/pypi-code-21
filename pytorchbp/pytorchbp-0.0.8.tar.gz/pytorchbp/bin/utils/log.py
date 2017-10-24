from inspect import currentframe, getframeinfo
import sys

class log(suppress_warnings = False):
    def warning(message = "No message provided.")
        if not suppress_warnings:
            print("WARNING:", message)
            print(frameinfo.filename, frameinfo.lineno)

    def error(message = "No message provided.")
        print("ERROR:", message)
        print(frameinfo.filename, frameinfo.lineno)
        sys.exit(1)