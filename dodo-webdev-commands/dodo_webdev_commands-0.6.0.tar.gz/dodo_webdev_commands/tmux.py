# noqa
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.framework import CommandError
from plumbum import local
import os


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('--only-kill', action='store_true')

    def _live_container_names(self):
        docker = local['docker']
        container_names = self.get_config('/TMUX/docker_kill', [])
        live_docker_containers = docker('ps')
        return [x for x in container_names if x in live_docker_containers]

    def _exited_container_names(self):
        docker = local['docker']
        container_names = self.get_config('/TMUX/docker_kill', [])
        live_docker_containers = docker('ps')
        exited_docker_containers = docker('ps', '-a')
        return [
            x for x in container_names
            if x in exited_docker_containers
            and x not in live_docker_containers
        ]

    def handle_imp(self, only_kill, **kwargs):  # noqa
        check_exists = self.get_config('/TMUX/check_exists', '/')
        if not os.path.exists(check_exists):
            raise CommandError("Path %s does not exist" % check_exists)

        live_container_names = self._live_container_names()
        if live_container_names:
            self.runcmd(['docker', 'kill'] + live_container_names)

        exited_container_names = self._exited_container_names()
        if exited_container_names:
            self.runcmd(['docker', 'rm'] + exited_container_names)

        if not only_kill:
            default_script = os.path.join(
                self.get_config("/ROOT/res_dir"),
                "tmux.sh"
            )
            tmux_script = self.get_config("/TMUX/script_file", default_script)
            self.runcmd(["chmod", "+x", tmux_script])
            self.runcmd([tmux_script])
