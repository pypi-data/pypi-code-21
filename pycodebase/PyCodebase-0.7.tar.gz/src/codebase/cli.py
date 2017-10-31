import argparse
import logging

import codebase
from . import commands



# Codebase's API returns 20 per page.
DEFAULT_LIMIT = 20


def create_parser():
    parser = argparse.ArgumentParser(prog='codebase')
    parser.add_argument('--debug', action='store_true', default=False)

    subparsers = parser.add_subparsers()
    # codebase <action> <project> --format=[json|csv]

    activity_parser = subparsers.add_parser('activity')
    activity_parser.set_defaults(func=commands.activity)
    activity_parser.add_argument('project', nargs='?')
    activity_parser.add_argument('--format', choices=['json', 'csv'], default='csv')
    activity_parser.add_argument('--limit', type=int, default=DEFAULT_LIMIT)

    ticket_parser = subparsers.add_parser('ticket')
    ticket_parser.set_defaults(func=commands.ticket)
    ticket_parser.add_argument('project')
    ticket_parser.add_argument('--format', choices=['json', 'csv'], default='csv')
    ticket_parser.add_argument('--limit', type=int, default=DEFAULT_LIMIT)

    return parser


def main(argv):
    parser = create_parser()
    opts = parser.parse_args(argv[1:])

    if opts.debug:
        logging.basicConfig(level=logging.DEBUG)

    cb = codebase.Client.with_secrets('~/.codebase_secrets.ini')
    opts.func(cb, opts)
