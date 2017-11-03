from __future__ import print_function

import os
import sys
import tempfile
import argparse

from darpy.version import __version__

PIP_CMD = 'pip --isolated --no-cache-dir'

_PIP_DOWNLOAD_CMD = PIP_CMD + ' download --dest "{}"'
PIP_DOWNLOAD_SRC_CMD = PIP_CMD + ' download --dest "{}" -e "{}"'
PIP_DOWNLOAD_REQ_CMD = PIP_CMD + ' download --dest "{}" -r "{}"'

PIP_INSTALL_CMD = (
    PIP_CMD +
    ' install --no-index --find-links "{0}" --ignore-installed "{0}"/*')
CWD = os.getcwd()


def _run(cmd):
    print(cmd, file=sys.stderr)
    os.system(cmd)


def execute_pack(args):
    packdir = tempfile.mkdtemp()
    print('packing into {}'.format(packdir), file=sys.stderr)
    for src in args.src:
        _run(PIP_DOWNLOAD_SRC_CMD.format(packdir, src))
    for req in args.requirements:
        _run(PIP_DOWNLOAD_REQ_CMD.format(packdir, req))
    _run('tar -C "{}" -czf "{}" .'
         .format(packdir, os.path.join(CWD, 'darpy-pack.tgz')))
    _run('rm -r "{}"'.format(packdir))


def execute_unpack(args):
    unpackdir = tempfile.mkdtemp()
    print('unpacking into {}'.format(unpackdir), file=sys.stderr)
    _run('tar -C "{}" -xzf "{}" .'.format(unpackdir, args.PKG_FILE))
    if args.virtualenv:
        pip_prefix = os.path.join(args.virtualenv, 'bin/python') + ' -m '
    else:
        pip_prefix = ''
    _run(pip_prefix + PIP_INSTALL_CMD.format(unpackdir))
    _run('rm -r "{}"'.format(unpackdir))


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
    unpack_parser.add_argument(
        '--virtualenv', help=('Unpack into virtualenv (as opposed to whatever '
                              'the current `pip` is wired up to)'))

    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
