# noqa
import argparse
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.framework.util import remove_trailing_dashes


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('--playbook')
        parser.add_argument('server')
        parser.add_argument(
            'ansible_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, server, playbook, ansible_args, **kwargs):  # noqa
        playbook = playbook or self.get_config("/ANSIBLE/default_playbook")
        self.runcmd(
            [
                "ansible-playbook",
                "-i", "hosts",
                playbook,
                "-l", server
            ]
            + remove_trailing_dashes(ansible_args),
            cwd=self.get_config("/ANSIBLE/src_dir")
        )
