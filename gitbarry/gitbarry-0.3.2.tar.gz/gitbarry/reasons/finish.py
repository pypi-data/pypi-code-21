from .abstract import AbstractReason
from gitbarry.config import settings
from gitbarry.utils import git, shortcuts


class Reason(AbstractReason):
    def usage(self):
        print("git barry finish options:")
        print("  git barry finish")

    def validate(self):
        if len(self.args) != 0:
            return ['use git barry start help to see options.']
        return []

    def run(self):
        shortcuts.ensure_current_branch_is_taskbranch()
        task_type = shortcuts.get_current_task_type()
        print("Current branch is %s" % task_type)
        task_params = settings["TASKS"][task_type]
        finish_action = task_params['finish-action']
        action_module = settings['FINISH_ACTIONS'][finish_action]
        action = action_module.Action(task_params)
        action.run()

        switch_to = task_params.get('finish-branch', task_params['branch-from'])
        git.swith_to_branch(switch_to)
        print("Done")
