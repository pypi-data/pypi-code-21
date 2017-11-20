"""CLI for pynclose.

"""

import os
import argparse


def parse_args(args:iter=None) -> dict:
    return cli_parser().parse_args(args)


def cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('infile', type=existant_file,
                        help='file containing the context data')
    parser.add_argument('--min-ext', '-e', type=int, default=1,
                        help="minimal number of object in concepts")
    parser.add_argument('--min-int', '-i', type=int, default=1,
                        help="minimal number of attributes in concepts")
    parser.add_argument('--outfile', '-o', type=str, default=None,
                        help="lp file to write the atoms in (default: stdout)")
    return parser

def existant_file(filepath:str) -> str:
    """Argparse type, raising an error if given file does not exists"""
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError("file {} doesn't exists".format(filepath))
    return filepath


