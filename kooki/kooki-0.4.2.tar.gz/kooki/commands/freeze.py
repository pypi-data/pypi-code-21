import yaml
from kooki.version import __version__

from kooki.config_file_parser import parse_args
from kooki.kitchen import freeze_jars, freeze_kooki, check_kooki_freeze, apply_kooki_freeze
from kooki.tools import write_file, read_file

from .command import Command

__command__ = 'freeze'
__description__ = 'Freeze version of Kooki and Jars'

class FreezeCommand(Command):

    def __init__(self):
        super(FreezeCommand, self).__init__(__command__, __description__)
        self.add_argument('documents', nargs='*')
        self.add_argument('-f', '--config-file', default='kooki.yaml')

    def callback(self, args):
        documents = parse_args(args)
        freeze_kooki(__version__)

        jars = {}
        for name, document in documents.items():
            jars.update(freeze_jars(document))

        repositories = {
            'kooki': __version__,
            'repositories': jars}
        write_file('.kooki_freeze', yaml.safe_dump(repositories, default_flow_style=False))
