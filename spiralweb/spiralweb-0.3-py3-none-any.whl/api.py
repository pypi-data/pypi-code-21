import sys
from .parser import parse_webs
from .model import SpiralWeb

def parseSwFile(path):
    handle = None

    if path == None:
        handle = sys.stdin
        path = 'stdin'
    else:
        handle = open(path, 'r')

    fileInput = handle.read()
    handle.close()

    chunkList = parse_webs({path: fileInput})[path]

    return SpiralWeb(chunks=chunkList)
