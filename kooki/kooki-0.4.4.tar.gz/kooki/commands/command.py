import argparse, traceback

from kooki.tools.output import Output
from kooki import DocumentException

class Command:

    def __init__(self, command, description):
        self.command = command

        self.parser = argparse.ArgumentParser(prog=self.command, description=description, add_help=False)
        self.parser.set_defaults(callback=self)

        self.parser.add_argument('-d', '--debug', help='Show information to help debug the bake processing', action='store_true')
        self.parser.add_argument('--no-color', help='The output has no color.', action='store_true')
        self.parser.add_argument('--no-output', help='There is no output.', action='store_true')
        self.subparsers = None

    def add_command(self, command, description='', help=''):
        if self.subparsers == None:
            self.subparsers = self.parser.add_subparsers(help=help)
        subparser = self.subparsers.add_parser(command.parser.prog, help=command.parser.description)
        subparser.__dict__ = command.parser.__dict__;

    def add_argument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def __call__(self, args):
        try:
            Output.start_command(self.command)
            Output.set_output_policy(not args.no_output)
            Output.set_color_policy(not args.no_color)
            Output.set_debug_policy(args.debug)

            self.callback(args)

        except RuntimeError as e:
            print(e)

        except DocumentException as e:
            Output.error_step('Errors')
            Output.error(e)

        except Exception as e:
            Output.error_step('Errors')
            Output.error(traceback.format_exc()[:-1])

        finally:
            Output.end_command()
