from __future__ import print_function

import argparse

import os
import sys

from darpy.version import __version__


def darpy_run(cmd):
    print(cmd, file=sys.stderr)
    os.system(cmd)


def make_parser():
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

    return parser, subparsers
