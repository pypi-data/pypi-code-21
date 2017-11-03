""":mod:`main` module defines the main :mod:`latest` command line script.

"""

from __future__ import print_function

import sys
import argparse

from .config import create_config
from .config import config as Config
from .shortcuts import render
from .exceptions import ContextError, PyExprSyntaxError


def main():
    args = parse_args()
    output = process(args)
    write(output, args)


def parse_args():
    parser = argparse.ArgumentParser(description='A LaTeX-oriented template engine.')
    parser.add_argument('template', help='path to template file.')
    parser.add_argument('data', help='path to data file.')
    parser.add_argument('--output', '-o', help='path to output file; default to stdout.')
    parser.add_argument('--config', '-c', help='path to configuration file; default to ~/.latest/latest.cfg.')
    return parser.parse_args()


def process(args):
    config = create_config(config_file=args.config) if args.config else Config
    try:
        return render(args.template, args.data, config=config)
    except (ContextError, PyExprSyntaxError) as e:
        print(e, file=sys.stderr)
        print("\n" + e.report, file=sys.stderr)
        sys.exit(-1)


def write(output, args):
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)
