from .abstract import AbstractAction
from gitbarry.utils import git


class Action(AbstractAction):
    def init(self):
        pass

    def run(self):
        current_branch = git.get_current_branch()
        _, ver = current_branch.split("/")
        git.tag(ver)
