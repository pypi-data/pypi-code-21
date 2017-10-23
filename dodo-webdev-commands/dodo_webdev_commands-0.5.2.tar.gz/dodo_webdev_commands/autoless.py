# noqa
import argparse
from dodo_commands.system_commands import DodoCommand
from dodo_commands.framework.util import remove_trailing_dashes

class Command(DodoCommand):  # noqa
    help = ""
    docker_options = [
        ('name', 'autoless'),
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'autoless_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, autoless_args, **kwargs):  # noqa
        autoless = self.get_config("/LESS/autoless", "autoless")
        self.runcmd(
            [
                "mkdir",
                "-p",
                self.get_config("/LESS/output_dir")
            ]
        )

        self.runcmd(
            [
                autoless,
                ".",
                self.get_config("/LESS/output_dir")
            ] + remove_trailing_dashes(autoless_args),
            cwd=self.get_config("/LESS/src_dir")
        )
