#!/usr/bin/env python
from optparse import OptionParser
from procgraph import logger
from procgraph.utils import wrap_script_entry_point
from procgraph_mplayer.conversions.video_info import pg_video_info
from pprint import pformat


usage = """
    %cmd  [-o <output>] <filename>
"""


def video_info_main(args):
    parser = OptionParser(usage=usage)

#     parser.add_option("-o", dest='output', type="string",
#                       help='Output video.')

    (_, args) = parser.parse_args(args)

    if len(args) != 1:
        msg = 'Exactly one argument necessary.'
        raise Exception(msg)

    filename = args[0]
    
    info = pg_video_info(filename)

    print pformat(info)
    
    return 0


def main():
    wrap_script_entry_point(video_info_main, logger)

if __name__ == '__main__':
    main()
