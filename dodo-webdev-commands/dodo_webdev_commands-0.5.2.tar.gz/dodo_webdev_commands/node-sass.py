# noqa
import argparse
from dodo_commands.system_commands import DodoCommand
import os

class Command(DodoCommand):  # noqa
    help = ""
    docker_options = [
        ('name', 'node-sass'),
    ]

    def _cmd_str(self, args):
        nodesass = self.get_config("/SASS/nodesass", "node-sass")
        cmds = []
        for src_file, output_file in self.get_config("/SASS/src_map").items():
            cmds.append("{nodesass} {src_file} {output_file} {args}".format(
                nodesass=nodesass,
                src_file=src_file,
                output_file=output_file,
                args=" ".join(args)
            ))
        return " & ".join(cmds)

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('--watch', action="store_true")
        parser.add_argument(
            'nodesass_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, watch, nodesass_args, **kwargs):  # noqa
        for src_file, output_file in self.get_config("/SASS/src_map").items():
            self.runcmd(
                [
                    "mkdir",
                    "-p",
                    os.path.dirname(output_file)
                ]
            )

        self.runcmd(["/bin/bash", "-c", self._cmd_str(nodesass_args)])
        if watch:
            self.runcmd(["/bin/bash", "-c", self._cmd_str(nodesass_args + ['-w'])])
