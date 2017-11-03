from gitbarry.constants import FINISH_ACTIONS

def validate_settings(settings: dict):
    pass

def validate_task(task_params: dict):
    errors = []
    if 'branch-from' not in task_params:
        errors.append("'branch-from' not found in task params")

    finish_action = task_params.get('finish-action', None)
    if finish_action not in FINISH_ACTIONS.keys():
        errors.append("Unknown finish-action value - '%s'. %s is valid" % (finish_action, "|".join(list(FINISH_ACTIONS.keys()))))

    return errors

