import argparse
import sys
import mingle


def __get_arg_parser():
    parser = argparse.ArgumentParser(description="Inter-mingle the contents of several log files by date stamp.")
    parser.add_argument("files", nargs='+', help="the files to intermingle")
    parser.add_argument("-q", "--quiet", help="strip the filename annotations from the output", action="store_true")
    parser.add_argument("-v", "--verbose", help="Show traceback on error", action="store_true")
    return parser


def main():
    parser = __get_arg_parser()
    args = parser.parse_args()

    try:
        mingle.cat(args.files, label=not args.quiet)
    except Exception as e:
        if args.verbose:
            raise
        sys.exit("Encountered Error: {}".format(e))
