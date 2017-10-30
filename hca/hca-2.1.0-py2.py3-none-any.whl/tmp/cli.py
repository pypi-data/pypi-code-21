# coding: utf-8

"""
Human Cell Atlas Command Line Interface
"""

import argparse, sys, json, os

import requests, six

import hca.dss.cli
from hca.dss.constants import Constants
from hca.dss.argument_parser import NonPrintingParser, PrintingException


class CLI:

    def __init__(self):
        self.parser = self._setup_arg_parser()

        # Windows includes carriage returns
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    def run(self):
        args = self.parser.parse_args(sys.argv[1:])
        func = args.func
        del args.func
        func(args)

    def _setup_arg_parser(self):
        uber_parser = argparse.ArgumentParser(description=__doc__,
                                              formatter_class=argparse.RawDescriptionHelpFormatter)
        subparsers = uber_parser.add_subparsers(title="subcommands", description="valid commands",
                                                help="TODO subcommands")

        hca.dss.cli.add_commands(subparsers)

        # staging_parser = subparsers.add_parser('upload')
        # staging_subparsers = staging_parser.add_subparsers(help="TODO area subparsers help")
        # area_parser = staging_subparsers.add_parser('area')
        # area_parser.add_argument('creds')
        # stage_parser = staging_subparsers.add_parser('stage')
        # stage_parser.add_argument('file')
        # stage_parser.set_defaults(func=self.foo)
        return uber_parser

    def parse_args(self, args):
        args = self.parser.parse_args(args)
        args = vars(args)
        args = {key: value for key, value in args.items() if value is not None}
        func = args['func']
        del args['func']
        return func, args
