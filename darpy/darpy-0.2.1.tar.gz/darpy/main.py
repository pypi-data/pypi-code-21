from __future__ import print_function

from darpy.common import make_parser
from darpy.pack import add_pack_command
from darpy.unpack import add_unpack_command


def parse_args():
    parser, subparsers = make_parser()
    add_pack_command(subparsers)
    add_unpack_command(subparsers)
    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
