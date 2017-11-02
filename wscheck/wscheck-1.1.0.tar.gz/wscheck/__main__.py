#!/usr/bin/env python

"""Whitespace checking tool."""

import argparse
import os
import sys

from checker import WhitespaceChecker, RULES
from printer import ErrorPrinter
from version import Version


def main(*args):
    """
    :type args: str
    """
    parsed_args = _parse_args(args)

    if parsed_args.list_rules:
        _list_rules()
        return 0

    checker = WhitespaceChecker(excluded_rules=parsed_args.excludes)
    for file_path in parsed_args.paths:
        checker.check_file(file_path)

    printer = ErrorPrinter(parsed_args.paths, checker.issues)
    printer.print_to_tty()
    if parsed_args.output_checkstyle:
        printer.write_checkstyle(parsed_args.output_checkstyle)

    if checker.issues:
        return 1

    return 0


def _list_rules():
    row_template = '{:<6s} {}'
    print(row_template.format('[RULE]', '[MESSAGE]'))
    for rule, message in RULES.items():
        print(row_template.format(rule, message))


def _parse_args(args):
    """
    :type args: tuple[str]
    """
    def rule(rule_name):
        if rule_name not in RULES:
            raise argparse.ArgumentTypeError('Unknown rule')
        return rule_name

    parser = argparse.ArgumentParser(prog='wscheck', description=__doc__, version=Version().release,
                                     formatter_class=WideHelpFormatter)

    parser.add_argument('paths', type=str, nargs='*',
                        help='Path of files for test')
    parser.add_argument('-l', '--list-rules', dest='list_rules', action='store_true',
                        help='List rules')

    parser.add_argument('-e', '--exclude', dest='excludes', metavar='RULE', type=rule, nargs='+',
                        help='Exclude rule(s)')
    parser.add_argument('--checkstyle', dest='output_checkstyle', type=str,
                        help='Path of checkstyle output')

    parsed_args = parser.parse_args(args)

    if not parsed_args.list_rules and not parsed_args.paths:
        parser.error('paths')

    return parsed_args


class WideHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog, *args, **kwargs):
        indent_increment = 2
        max_help_position = 40
        width = int(os.getenv("COLUMNS", 120)) - 2

        super(WideHelpFormatter, self).__init__(prog, indent_increment, max_help_position, width)


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
