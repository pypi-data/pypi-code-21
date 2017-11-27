# noqa
import argparse
from dodo_commands.system_commands import DodoCommand
from dodo_commands.framework.util import remove_trailing_dashes


class Command(DodoCommand):  # noqa
    help = ""
    docker_options = [
        ('name', 'pytest'),
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'pytest_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, pytest_args, **kwargs):  # noqa
        no_capture = not self.get_config("/PYTEST/capture", True)
        html_report = self.get_config("/PYTEST/html_report", None)
        test_file = self.get_config("/PYTEST/test_file", None)

        self.runcmd(
            [
                self.get_config("/PYTEST/pytest", "pytest"),
            ] +
            remove_trailing_dashes(
                pytest_args +
                ([test_file] if test_file else []) +
                (["--capture", "no"] if no_capture else []) +
                (["--html", html_report] if html_report else [])
            ),
            cwd=self.get_config(
                "/PYTEST/src_dir",
                self.get_config("/ROOT/src_dir")
            )
        )
