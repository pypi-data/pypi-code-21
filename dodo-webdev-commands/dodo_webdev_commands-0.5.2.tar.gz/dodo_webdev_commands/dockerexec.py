# noqa
from dodo_commands.system_commands import DodoCommand


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('name')

    def handle_imp(self, name, **kwargs):  # noqa
        self.runcmd(
            [
                'docker',
                'exec',
                '-i',
                '-t',
                name,
                '/bin/bash',
            ],
        )
