import sys
import argparse
import string  # For generating a temp file for stdin
import random  # For generating a temp file for stdin
from __init__ import __version__ as ipwbVersion
from util import INDEX_FILE

# ipwb modules
import replay
import indexer
import util

from util import IPFSAPI_IP, IPFSAPI_PORT, IPWBREPLAY_IP, IPWBREPLAY_PORT


def main():
    args = checkArgs(sys.argv)


def checkArgs_index(args):
    if not util.isDaemonAlive():
        sys.exit()
    encKey = None
    compressionLevel = None
    if args.e:
        encKey = ''
    if args.c:
        compressionLevel = 6  # Magic 6, TA-DA!

    indexer.indexFileAt(args.warcPath, encKey, compressionLevel,
                        args.compressFirst, debug=args.debug)


def checkArgs_replay(args):
    likelyPiping = not sys.stdin.isatty()
    if likelyPiping:
        cdxjIn = ''.join(sys.stdin.readlines())

        # Write data to temp file (sub-optimal)
        tempFilePath = '/tmp/' + ''.join(random.sample(
              string.ascii_uppercase + string.digits * 6, 6)) + '.cdxj'
        with open(tempFilePath, 'w') as f:
            f.write(cdxjIn)
        args.index = tempFilePath

    # TODO: add any other sub-arguments for replay here
    if hasattr(args, 'index') and args.index is not None:
        replay.start(cdxjFilePath=args.index)
    else:
        replay.start()


def checkArgs(argsIn):
    """
    Check to ensure valid arguments were passed in and provides guidance
    on the available options if not
    """
    parser = argparse.ArgumentParser(
        description='InterPlanetary Wayback (ipwb)', prog="ipwb")
    subparsers = parser.add_subparsers(
        title="ipwb commands",
        description="Invoke using \"ipwb <command>\", e.g., ipwb replay")

    indexParser = subparsers.add_parser(
        'index',
        prog="ipwb",
        description="Index a WARC file for replay in ipwb",
        help="Index a WARC file for replay in ipwb")
    indexParser.add_argument(
        'warcPath',
        help="Path to a WARC[.gz] file",
        metavar="index <warcPath>",
        nargs='+',
        default=None)
    indexParser.add_argument(
        '-e',
        help="Encrypt WARC content prior to disseminating to IPFS",
        action='store_true',
        default=False)
    indexParser.add_argument(
        '-c',
        help="Compress WARC content prior to disseminating to IPFS",
        action='store_true',
        default=False)
    indexParser.add_argument(
        '--compressFirst',
        help="Compress data before encryption, where applicable",
        action='store_true',
        default=False)
    indexParser.add_argument(
        '--debug',
        help="Convenience flag to help with testing and debugging",
        action='store_true',
        default=False)
    indexParser.set_defaults(func=checkArgs_index)
    replayParser = subparsers.add_parser(
        'replay',
        prog="ipwb replay",
        help="Start the ipwb replay system")
    replayParser.add_argument(
        'index',
        help="CDXJ file to use for replay",
        nargs='?')
    replayParser.set_defaults(func=checkArgs_replay)

    parser.add_argument(
        '-d', '--daemon',
        help='Location of ipfs daemon (default 127.0.0.1:5001)',
        default='{0}:{1}'.format(IPFSAPI_IP, IPFSAPI_PORT),
        dest='daemon_address')
    parser.add_argument(
        '-o', '--outfile',
        help='Filename of newly created CDXJ index file')
    parser.add_argument(
        '-v', '--version', help='Report the version of ipwb', action='version',
        version='InterPlanetary Wayback ' + ipwbVersion)

    if len(argsIn) == 1:
        parser.print_help()
        sys.exit()
    # parser.add_argument('replay',
    #   help="Index a WARC file", default=None, nargs='?')
    # parser.add_argument('--index', help="Index a WARC file",
    #  default=None, nargs=1)
    # parser.add_argument('warcPath', help="Path to a WARC[.gz] file")
    results = parser.parse_args()
    results.func(results)

    return results


if __name__ == "__main__":
    main()
