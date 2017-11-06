import argparse

parser = argparse.ArgumentParser(prog="neuropredict")

parser.add_argument('-u', '--userdirs', action='store', dest='userdir', nargs='+', help='set of userdefined features')
parser.add_argument('-b')
parser.add_argument('-f')

print(parser.parse_args())


