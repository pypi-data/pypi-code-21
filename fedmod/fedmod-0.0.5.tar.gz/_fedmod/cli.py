import sys
import argparse
import logging

from .module_generator import ModuleGenerator
from . import _depchase, _repodata

# TODO: Switch this over to click (already a dependency for progress bars)

class ModtoolsCLI(object):
    """ Class for processing data from commandline """

    @staticmethod
    def build_parser():
        parser = argparse.ArgumentParser(description="Generates module related files")
        base_parser = argparse.ArgumentParser(add_help=False)
        base_parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="verbose operation"
        )

        subparsers = parser.add_subparsers(dest="cmd_name")

        parser_rpm2module = subparsers.add_parser(
            'rpm2module', parents=[base_parser],
            help="Generates modulemd file",
            description="Gets package info and dependencies and creates modulemd file."
        )
        parser_rpm2module.add_argument(
            "--output",
            "-o",
            metavar="FILE",
            dest="output_fname",
            help="Write to FILE instead of stdout."
        )
        parser_rpm2module.add_argument(
            "--build-deps",
            metavar="N",
            default=0,
            dest="build_deps_iterations",
            help="Attempt to ensure N levels of build dependencies (Default: %(default)s)."
        )
        parser_rpm2module.add_argument(
            "pkgs",
            metavar='PKGS',
            nargs='+',
            help="Specify list of packages for module.",
        )

        parser_metadata = subparsers.add_parser(
            'fetch-metadata', parents=[base_parser],
            help="Fetches repository metadata",
            description="Caches needed repository metadata locally"
        )

        return parser

    def __init__(self, args=None):
        self.parser = ModtoolsCLI.build_parser()
        self.args = self.parser.parse_args(args)

    def __getattr__(self, name):
        try:
            return getattr(self.args, name)
        except AttributeError:
            return object.__getattribute__(self, name)


def run():
    try:
        cli = ModtoolsCLI(sys.argv[1:])
        if cli.args.verbose:
            logging.basicConfig(level=logging.INFO)
        if cli.args.cmd_name == 'rpm2module':
            mg = ModuleGenerator(cli.args.pkgs)
            mg.run(cli.args.output_fname, cli.args.build_deps_iterations)
        elif cli.args.cmd_name == 'fetch-metadata':
            _repodata.download_repo_metadata()

    except KeyboardInterrupt:
        print('\nInterrupted by user')
    except Exception as e:
        logging.exception("Unexpected exception")
        sys.exit(1)
