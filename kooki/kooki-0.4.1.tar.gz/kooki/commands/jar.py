import argparse, os, sys

from kooki.tools.output import Output
from kooki.kitchen import get_jars
from .command import Command

__command__ = 'jar'
__description__ = 'List jars'

class JarCommand(Command):

    def __init__(self):
        super(JarCommand, self).__init__(__command__, __description__)

    def callback(self, args):

        jars = get_jars()

        Output.start_step('jars')
        for jar in jars:
            Output._print_colored(jar, 'blue')
            Output._print_colored('  version: ', 'yellow', end='')
            Output._print_colored(jars[jar]['version'], 'green')
