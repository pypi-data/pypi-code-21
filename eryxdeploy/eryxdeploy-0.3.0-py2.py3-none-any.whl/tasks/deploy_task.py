from fabric.state import env
from fabric.tasks import Task


class DeployTask(Task):
    """
    Deploy after-push upgrades on a remote stack
    """
    name = 'deploy'

    def run(self):
        remote_stack = env.stacks[env.env]
        remote_stack.upgrade()
