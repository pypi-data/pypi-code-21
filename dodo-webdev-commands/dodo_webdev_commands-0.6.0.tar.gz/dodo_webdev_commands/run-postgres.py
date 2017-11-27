# noqa
from dodo_commands.extra.standard_commands import DodoCommand


class Command(DodoCommand):  # noqa
    help = ""
    docker_options = [
        ('name', 'pg'),
    ]

    def handle_imp(self, **kwargs):  # noqa
        self.runcmd(
            [
                "sudo", "-u", "postgres",
                "/usr/lib/postgresql/9.5/bin/postgres",
                "-D" "/var/lib/postgresql/9.5/main",
                "-c", "config_file=/etc/postgresql/9.5/main/postgresql.conf",
            ],
            cwd="/"
        )
