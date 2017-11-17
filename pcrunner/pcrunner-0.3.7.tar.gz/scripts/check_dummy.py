#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai
# scripts/check_dummy.py

"""
A simple Nagios plugin for testing purposes.
"""

import time
import sys
from argparse import ArgumentParser


def main(args):
    if args.exitcode >= 0 and args.exitcode < 4:
        if args.sleep:
            time.sleep(args.sleep)
        if args.text:
            print((args.text))
        sys.exit(args.exitcode)
    else:
        raise Exception('exit code should be >= 0 and < 4')


def parse_args(args):
    """ Parse the command-line arguments to pcrunner. """

    parser = ArgumentParser(description='check_dummy.py')
    parser.add_argument(
        "exitcode",
        type=int,
        help="Exit code or return code: A number the program returns on exit",
    )
    parser.add_argument(
        "text",
        type=str,
        nargs='?',
        default='',
        help="Text which the program prints",
    )
    parser.add_argument(
        "-s",
        "--sleep",
        type=int,
        help="Time in seconds the program will wait before exiting",
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    main(args)
