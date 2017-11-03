import sys
import importlib
from .git import get_current_branch


def import_from_str(module: str):
    return importlib.import_module(module)


def get_current_task_type():
    from gitbarry.config import settings

    current_branch = get_current_branch()
    for task_prefix in settings['TASKS'].keys():
        if current_branch.startswith('%s/' % task_prefix):
            return task_prefix
    return False


def ensure_current_branch_is_taskbranch():
    current_task_type = get_current_task_type()
    if current_task_type is False:
        print("Current branch not looks like barry task branch.")
        sys.exit(5)
