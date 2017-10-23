# noqa
import argparse
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.framework.util import remove_trailing_dashes


class Command(DodoCommand):  # noqa
    docker_options = [
        ('name', 'django-runserver'),
        ('publish', '8000:8000'),
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'runserver_args',
            nargs=argparse.REMAINDER
        )

    def handle_imp(self, runserver_args, *args, **kwargs):  # noqa

        self.runcmd(
            [
                self.get_config("/DJANGO/python"),
                "manage.py",
                "runserver", "0.0.0.0:8000",
            ]
            + remove_trailing_dashes(runserver_args)
            + self.get_config("/DJANGO/runserver_args", []),
            cwd=self.get_config("/DJANGO/src_dir")
        )
