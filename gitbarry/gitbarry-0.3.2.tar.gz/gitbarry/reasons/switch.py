from .abstract import AbstractReason
from gitbarry.config import settings
from gitbarry.utils import git
tasks = settings['TASKS'].keys()


class Reason(AbstractReason):
    def usage(self):
        print("git barry switch options:")
        print("  git barry switch <task>/<feature_name>")

    def validate(self):
        if len(self.args) != 1:
            return ['use "git barry switch help" to see options.']
        branch = self.args[0]
        if git.get_current_branch() == branch:
            return [
                'Already at %s' % branch
            ]
        errors = []
        return errors

    def run(self):
        branch = self.args[0]
        git.swith_to_branch(branch)
        print("Done")
