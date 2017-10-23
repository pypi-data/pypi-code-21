# noqa
from dodo_commands.extra.standard_commands import DodoCommand
from plumbum.cmd import docker


class Command(DodoCommand):  # noqa
    help = ""
    safe = False

    docker_rm = False
    docker_options = [
        ('name', 'dockerupdate')
    ]

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('--playbook')
        parser.add_argument('--tags')

    def _playbook(self, playbook):
        return playbook or self.get_config("/ANSIBLE/default_playbook")

    @property
    def _ansible_dir(self):
        return self.get_config("/ANSIBLE/src_dir")

    @property
    def _remote_ansible_dir(self):
        return "/root/ansible/"

    def _tags(self, tags):
        return ["--tags=%s" % tags] if tags else []

    def handle_imp(self, playbook, tags, **kwargs):  # noqa
        self.docker_options.append(
            ('volume', '%s:%s' % (self._ansible_dir, self._remote_ansible_dir))
        )

        self.runcmd(
            [
                "ansible-playbook",
                "-i", "hosts",
                "-l", "localhost",
                self._playbook(playbook)
            ] +
            self._tags(tags),
            cwd=self._remote_ansible_dir
        )

        container_id = docker("ps", "-l", "-q")[:-1]
        docker("commit", container_id, self.get_config("/DOCKER/image"))
        docker("rm", container_id)
