#!/usr/bin/env python
from optparse import OptionParser
from procgraph import logger
from procgraph.utils import wrap_script_entry_point
from pprint import pformat
from procgraph_mplayer.conversions.video_convert import pg_video_convert


usage = """
    %cmd  [-o <output>] <filename>
"""


def video_convert_main(args):
    parser = OptionParser(usage=usage)

#     parser.add_option("-o", dest='output', type="string",
#                       help='Output video.')

    (_, args) = parser.parse_args(args)

    if len(args) != 2:
        msg = 'Exactly 2 arguments necessary.'
        raise Exception(msg)

    filename1 = args[0]
    filename2 = args[1]
    
    info = pg_video_convert(filename1, filename2)

    print pformat(info)
    
    return 0


def main():
    wrap_script_entry_point(video_convert_main, logger)

if __name__ == '__main__':
    main()
