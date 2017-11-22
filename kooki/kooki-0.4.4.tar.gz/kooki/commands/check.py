import yaml
from kooki.version import __version__

from kooki.kitchen import check_kooki_freeze
from kooki.tools import read_file

from .command import Command

__command__ = 'check'
__description__ = 'Check version of kooki freeze'

class CheckCommand(Command):

    def __init__(self):
        super(CheckCommand, self).__init__(__command__, __description__)

    def callback(self, args):
        freeze_file = read_file('.kooki_freeze')
        freeze_data = yaml.safe_load(freeze_file)
        check_kooki_freeze(__version__, freeze_data)
