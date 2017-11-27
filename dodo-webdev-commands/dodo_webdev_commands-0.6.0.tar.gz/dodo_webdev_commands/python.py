# noqa
from dodo_commands.system_commands import DodoCommand


class Command(DodoCommand):  # noqa
    help = ""
    docker_options = [
        ('name', 'python')
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('script')

    def handle_imp(self, script, **kwargs):  # noqa
        self.runcmd(
            [
                self.get_config('/PYTHON/python'),
                script,
            ],
            cwd=self.get_config('/PYTHON/src_dir')
        )
