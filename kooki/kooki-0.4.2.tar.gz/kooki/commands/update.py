import yaml

from kooki.kitchen import apply_kooki_freeze
from kooki.tools import read_file

from .command import Command

__command__ = 'update'
__description__ = 'Update a kooki project'

class UpdateCommand(Command):

    def __init__(self):
        super(UpdateCommand, self).__init__(__command__, __description__)

    def callback(self, args):
        freeze_file = read_file('.kooki_freeze')
        freeze_data = yaml.safe_load(freeze_file)
        apply_kooki_freeze(freeze_data, freeze_file)
