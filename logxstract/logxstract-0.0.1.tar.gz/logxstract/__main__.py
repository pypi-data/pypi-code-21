# -*- coding:utf-8 -*-
from argparse import ArgumentParser
import sys
import time

from lib import (
    add_arguments,
    extract_xml_from_file
)


def main():
    parser = ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    if not args.pid:
        print("Please specify (-p 30031223)")
        sys.exit()
    elif not args.file:
        print("Please specify file (-f 'filename.log')")
        sys.exit()
    start = time.time()
    extract_xml_from_file(
        str(args.pid),
        args.file,
        encoding=args.encoding or None
    )
    print('{} seconds elapsed'.format(time.time() - start))


if __name__ == '__main__':
    main()
