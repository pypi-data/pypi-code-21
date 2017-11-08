from argparse import ArgumentParser
from .utils import import_class
from . import __version__


class Main(object):

    def __init__(self):
        self.parsers = dict()
        self.parser = ArgumentParser(
            description='1C %(prog)s script.', prog="Utilites"
        )
        self.subparsers = self.parser.add_subparsers(
            help="Help for commands"
        )
        self._create_command("backup", "Backup/Restore utility")

    def _create_command(self, name, help):
        loader = self.get_loader(name)
        parser = self.subparsers.add_parser(
            name, help=help
        )
        parser.add_argument(
            "-b", "--backend", help="Utility-command backend",
            choices=loader.list()
        )
        parser.add_argument(
            "-v", "--version", help="1C %(prog)s script version.",
            default=False, action="store_true"
        )
        loader.add_arguments(parser)
        parser.set_defaults(command=name)
        self.parsers[name] = parser
        return parser

    def get_loader(self, name):
        return import_class("utilites_1c.{}.backends.Loader".format(name))()

    def __call__(self):
        args = self.parser.parse_args()
        if args.version:
            print(__version__)
            return
        try:
            command = args.command
            return self.get_loader(command).run(args)
        except AttributeError:
            self.parser.print_help()


main = Main()
