from __future__ import absolute_import, division, print_function
from .console import ConsoleHost
from .formattter import Formatter
from . import glb

import argparse
import copy


class extendAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):

        # if nargs == 0:
        #    raise ValueError('nargs for append actions must be > 0; if arg '
        #                     'strings are not supplying the value to append, '
        #                     'the append const action may be more appropriate')
        # if const is not None and nargs != OPTIONAL:
        #    raise ValueError('nargs must be %r to supply const' % OPTIONAL)
        super(extendAction, self).__init__(option_strings=option_strings,
                                           dest=dest,
                                           nargs=nargs,
                                           const=const,
                                           default=default,
                                           type=type,
                                           choices=choices,
                                           required=required,
                                           help=help,
                                           metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = copy.copy(getattr(namespace, self.dest, []))
        if items is None:
            items = []
        if values == []:
            values = ['all']
        for i in values:
            i = i.split(",")
            items.extend(i)
        setattr(namespace, self.dest, items)


def setDefaultArgs(argparser):
    defaults = argparser.add_argument_group(
        'Console options', 'Arguments unique to console')
    defaults.add_argument(["--show-color"],
                          action='store_true',
                          help="Show colored output")

    defaults.add_argument(["--disable-color"],
                          dest='show_color',
                          action='store_false',
                          help="Disable colored output")

    defaults.add_argument(["--verbose", "-v"],
                          action=extendAction,
                          nargs='*',
                          metavar="CATEGORY",
                          help="Display all verbose messages or only messages of provided categories")

    defaults.add_argument(["--debug"],
                          action=extendAction,
                          nargs='*',
                          metavar="CATEGORY",
                          help="Display all debug messages or only messages of provided categories")


def Setup(defaultHost=None, hosts=[]):
    glb.formatter = Formatter(defaultHost)
