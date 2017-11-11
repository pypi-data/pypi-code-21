import sys
from metadate import parse_date


def main():
    """ This is the function that is run from commandline with `metadate` """
    if "--lang" == sys.argv[1]:
        print(parse_date(" ".join(sys.argv[3:]), lang=sys.argv[2]))
    else:
        print(parse_date(" ".join(sys.argv[1:])))
