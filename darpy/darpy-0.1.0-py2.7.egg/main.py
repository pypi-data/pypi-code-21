from __future__ import print_function

import os
import sys
import tempfile
import argparse

from darpy.version import __version__

PIP_DOWNLOAD_CMD = 'pip --isolated --no-cache-dir download -d'


def _run(cmd):
    print(cmd, file=sys.stderr)
    os.system(cmd)


def execute_pack(args):
    packdir = tempfile.mkdtemp()
    print('packing into {}'.format(packdir), file=sys.stderr)
    for src in args.src:
        _run('{} "{}" -e "{}"'.format(PIP_DOWNLOAD_CMD, packdir, src))
    for req in args.requirements:
        _run('{} "{}" -r "{}"'.format(PIP_DOWNLOAD_CMD, packdir, req))


def execute_unpack(args):
    raise NotImplementedError


def parse_args():
    class SharedParser(argparse.ArgumentParser):
        def __init__(self, func=None, *args, **kwargs):
            argparse.ArgumentParser.__init__(self, *args, **kwargs)
            self.set_defaults(func=func)
            self.add_argument(
                '--version', action='version',
                version="%(prog)s " + __version__)

    parser = SharedParser(description='darpy')
    subparsers = parser.add_subparsers(
        title='Subcommands',
        parser_class=SharedParser, metavar='')

    pack_parser = subparsers.add_parser(
        'pack', func=execute_pack, help='Pack a Package')
    unpack_parser = subparsers.add_parser(
        'unpack', func=execute_unpack, help='UnPack a Package')

    pack_parser.add_argument(
        '--src', action='append', default=[],
        help='Add a package dir installable with pip')
    pack_parser.add_argument(
        '--requirements', action='append', default=[],
        help=('Add a requirements.txt file (`pip install -r` target) '
              'to the archive'))

    unpack_parser.add_argument(
        'PKG_FILE', help='An archive built with `darpy pack`')

    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
