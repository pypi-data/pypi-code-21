from .abstract import AbstractAction
from gitbarry.utils import git


class Action(AbstractAction):
    def init(self):
        print("Perform merge to %s" % self.params['finish-branch'])

    def run(self):
        current_branch = git.get_current_branch()
        git.swith_to_branch(self.params['finish-branch'])
        git.merge(current_branch)
