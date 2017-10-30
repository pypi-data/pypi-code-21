from fabric.state import env
from fabric.tasks import Task


class DeployTask(Task):
    name = 'deploy'

    def run(self):
        remote_stack = env.stacks[env.env]
        remote_stack.upgrade()
