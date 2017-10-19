#!/usr/bin/env python
from ..mp4conversion import convert_to_mp4
from optparse import OptionParser
from procgraph import logger
from procgraph.utils import wrap_script_entry_point


usage = """
    %cmd  [-o <output>] <filename>
"""


def tomp4(args):
    parser = OptionParser(usage=usage)

    parser.add_option("-o", dest='output', type="string",
                      help='Output video.')

    (options, args) = parser.parse_args(args)

    if len(args) != 1:
        msg = 'Exactly one argument necessary.'
        raise Exception(msg)

    filename = args[0]
    return convert_to_mp4(filename, mp4=options.output, quiet=True)


def main():
    wrap_script_entry_point(tomp4, logger)

if __name__ == '__main__':
    main()
