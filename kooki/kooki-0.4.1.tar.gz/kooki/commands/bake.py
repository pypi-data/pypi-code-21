import argparse

from kooki.config_file_parser import parse_args
from kooki import Kitchen

from .command import Command

__command__ = 'bake'
__description__ = 'Bake a kooki'

class BakeCommand(Command):

    def __init__(self):
        super(BakeCommand, self).__init__(__command__, __description__)
        self.add_argument('documents', nargs='*')
        self.add_argument('-f', '--config-file', default='kooki.yaml')
        self.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
        self.add_argument('-v', '--verbose', help='Show more information about the bake processing.', action='store_true')

    def callback(self, args):
        kitchen = Kitchen()
        documents = parse_args(args)

        for name, document in documents.items():
            kitchen.cook(name, document)
