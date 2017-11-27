# noqa
from dodo_commands.extra.standard_commands import DodoCommand


class Command(DodoCommand):  # noqa
    help = ""
    docker_options = [
        ('name', 'mongodb'),
    ]

    def handle_imp(self, **kwargs):  # noqa
        self.runcmd(
            [
                "sudo", "-u", "mongodb",
                "/usr/bin/mongod",
                "--bind_ip", "0.0.0.0",
                "--config", "/etc/mongod.conf",
            ],
            cwd="/"
        )
