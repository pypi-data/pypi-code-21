#!/usr/bin/env python
"""Command-line script for scanning codes from images.

Outputs as JSON to stdout.
"""
from __future__ import absolute_import, print_function

import argparse
import json
import logging
import os.path
import sys

# Fix Python path if scripts are run without pip-installing the quikklysdk package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quikklysdk import quikkly, quikklycore


log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-libs-dir', help='Path to quikklycore native libraries. You can also use the QUIKKLY_NATIVE_DIR environment variable.')

    # Output parameters
    parser.add_argument('--quiet', default=False, action='store_true', help='Avoid logging debug info to stderr.')

    # Input parameters
    parser.add_argument('--input-file', required=True, nargs='+', metavar='FILE', help='Input image file (can provide multiple)')

    args = parser.parse_args()
    check_args(parser, args)

    if not args.quiet:
        logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(levelname)s %(module)s:%(lineno)d: %(message)s')

    run_scanner(args)


def run_scanner(args):
    if args.native_libs_dir:
        quikkly.init(args.native_libs_dir)
    for fname in args.input_file:
        fname = os.path.abspath(fname)
        results = quikkly.scan_image_file(fname)
        log.info('%s: %d tags found.', fname, len(results))
        print(json.dumps(results))


def check_args(parser, args):
    for fname in args.input_file:
        if not os.path.exists(fname):
            parser.error('%s does not exist, cannot use as input file.' % fname)
        if os.path.isdir(fname):
            parser.error('%s is a directory, cannot use as input file.' % fname)
    try:
        quikklycore.check_numpy_pillow()
    except quikklycore.QuikklyImportError:
        parser.error('Failed to import numpy and Pillow Python packages, which are required for scanning.')


if __name__ == '__main__':
    main()
