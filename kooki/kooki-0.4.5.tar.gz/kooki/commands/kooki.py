import argparse, sys, platform

from kooki.version import __version__
from kooki.config_file_parser import parse_args
from kooki import Kitchen
from kooki.tools.output import Output

from .command import Command
from .bake import BakeCommand
from .freeze import FreezeCommand
from .update import UpdateCommand
from .check import CheckCommand
from .jar import JarCommand
from .new import NewCommand

__command__ = 'kooki'
__description__ = 'Generate easily any kind of documents.'

class KookiCommand(Command):

    def __init__(self):
        super(KookiCommand, self).__init__(__command__, __description__)
        self.add_argument('-v', '--version', help='Show program\'s version number and exit.', action='store_true')
        self.add_command(BakeCommand())
        self.add_command(FreezeCommand())
        self.add_command(CheckCommand())
        self.add_command(UpdateCommand())
        self.add_command(JarCommand())
        self.add_command(NewCommand())

    def callback(self, args):

        if args.version:
            Output._print_colored('Kooki', 'blue', end=' ')
            Output._print_colored(__version__, 'cyan')

            python_info = sys.version_info
            python_build = platform.python_build()
            Output._print_colored('Python', 'blue', end=' ')
            Output._print_colored('{0}.{1}.{2}'.format(python_info.major, python_info.minor, python_info.micro), 'cyan', end=' ')
            Output._print_colored('({0}, {1})'.format(python_build[0], python_build[1]), 'yellow')

            python_compiler = platform.python_compiler().split(' ')

            Output._print_colored(python_compiler[0], 'blue', end=' ')
            Output._print_colored(python_compiler[1], 'cyan', end=' ')
            Output._print_colored('({0})'.format(python_compiler[2]), 'yellow')
        else:
            print(self.parser.print_help())
