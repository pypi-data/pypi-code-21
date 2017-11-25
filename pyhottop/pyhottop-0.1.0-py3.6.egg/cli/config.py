#!/usr/bin/env python
"""Init the configuration for the toolset."""
__author__ = 'Brandon Dixon'
__version__ = '1.0.0'

from pyhottop.pyhottop import Hottop, SerialConnectionError
from argparse import ArgumentParser
import sys


def main():
    """Run the core."""
    parser = ArgumentParser()
    subs = parser.add_subparsers(dest='cmd')

    setup_parser = subs.add_parser('test')
    setup_parser.add_argument('--interface', default=None,
                              help='Manually pass in the USB connection.')
    args = parser.parse_args()

    if args.cmd == 'test':
        ht = Hottop()
        try:
            if args.interface:
                ht.connect(interface=args.interface)
            ht.connect()
        except SerialConnectionError as e:
            print("[!] Serial interface not accessible: %s" % str(e))
            sys.exit(1)
        print("[*] Successfully connected to the roaster!")

if __name__ == '__main__':
    main()
