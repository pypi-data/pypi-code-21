from spiralweb.api import parseSwFile
import parser
import argparse
import sys

def main():
    argparser = argparse.ArgumentParser(prog='spiralweb', description='Literate programming system')
    argparser.add_argument('--version', action='version', version='0.3')

    subparsers = argparser.add_subparsers(dest='command')

    tangle_parser = subparsers.add_parser('tangle', help='Extract source files from SpiralWeb literate webs')
    tangle_parser.add_argument('files', nargs=argparse.REMAINDER)

    weave_parser = subparsers.add_parser('weave', help='Generate documentation source files from SpiralWeb literate webs')
    weave_parser.add_argument('files', nargs=argparse.REMAINDER)

    help = subparsers.add_parser('help', help='Print help')

    options = argparser.parse_args()

    if options.command == 'help':
        argparser.print_help()
    else:
        if len(options.files) == 0:
            options.files.append(None)

        for path in options.files:
            try:
                web = parseSwFile(path)

                if options.command == 'tangle':
                    web.tangle()
                elif options.command == 'weave':
                    web.weave()
            except BaseException as e:
                print("ERROR: " + str(e))

if __name__ == '__main__':
    main()
