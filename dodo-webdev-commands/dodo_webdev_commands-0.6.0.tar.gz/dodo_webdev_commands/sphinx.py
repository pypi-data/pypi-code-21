# noqa
from dodo_commands.system_commands import DodoCommand
import os


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        pass

    def handle_imp(self, **kwargs):  # noqa
        output_dir = self.get_config('/SPHINX/output_dir')
        if not os.path.exists(output_dir):
            self.runcmd(['mkdir', '-p', output_dir])

        self.runcmd(
            [
                'sphinx-build',
                '-b',
                'html',
                self.get_config('/SPHINX/src_dir'),
                output_dir,
            ],
        )
