# noqa
import argparse
import os
from dodo_commands.system_commands import DodoCommand
from dodo_commands.framework.util import remove_trailing_dashes


class Command(DodoCommand):  # noqa
    help = ""
    docker_options = [
        ('name', 'tape'),
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'tape_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, tape_args, **kwargs):  # noqa
        webpack = self.get_config("/WEBPACK/webpack", "webpack")
        webpack_config = self.get_config("/TAPE/webpack_config")

        self.runcmd(
            [webpack, "--config", webpack_config],
            cwd=os.path.dirname(webpack_config)
        )
        self.runcmd(
            [
                self.get_config("/TAPE/tape"),
                self.get_config("/TAPE/bundle_file"),
            ] + remove_trailing_dashes(tape_args)
        )
