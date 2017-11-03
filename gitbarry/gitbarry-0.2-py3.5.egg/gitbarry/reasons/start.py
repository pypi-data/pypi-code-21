from .abstract import AbstractReason
from gitbarry.config import settings
from gitbarry.utils import git
tasks = settings['TASKS'].keys()


class Reason(AbstractReason):
    def usage(self):
        print("git barry start options:")
        print("  git barry start %s <feature_name>" % "|".join(tasks))

    def validate(self):
        if len(self.args) != 2:
            return ['use git barry start help to see options.']
        task, name = self.args
        errors = []
        if task not in tasks:
            errors.append("Unknown task for reason 'start': %s" % task)
        return errors

    def run(self):
        task, name = self.args
        task_params = settings["TASKS"][task]
        new_branch_name = '/'.join([task, name])

        git.swith_to_branch(task_params['branch-from'])
        git.create_new_branch(new_branch_name)
        git.merge(task_params['branch-from'])
        print("Done")
