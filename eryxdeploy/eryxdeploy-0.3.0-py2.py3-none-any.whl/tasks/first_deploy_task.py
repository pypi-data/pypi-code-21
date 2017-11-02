from fabric.state import env
from fabric.tasks import Task


class FirstDeployTask(Task):
    """
    Deploy a remote stack for the first time
    """
    name = 'first_deploy'

    def run(self):
        remote_stack = env.stacks[env.env]
        remote_stack.install()
