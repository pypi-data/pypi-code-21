from inspect import currentframe, getframeinfo
import sys

class logger():
    def __init__(self, suppress_warnings = False):
        self.suppress_warnings = suppress_warnings
        
    def warning(message = "No message provided."):
        if not self.suppress_warnings:
            print("WARNING:", message)
            print(frameinfo.filename, frameinfo.lineno)

    def error(message = "No message provided."):
        print("ERROR:", message)
        print(frameinfo.filename, frameinfo.lineno)
        sys.exit(1)