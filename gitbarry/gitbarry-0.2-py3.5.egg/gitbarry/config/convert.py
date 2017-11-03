import sys

from gitbarry.config import exceptions
from gitbarry.config.validator import validate_task
from gitbarry.constants import FINISH_ACTIONS

def config2settings(config) -> dict:
    settings = {
        'TASKS': {},
        'FINISH_ACTIONS': {},
    }

    for section in config.sections():
        if str(section).startswith('task-'): # Task
            task_name = str(section).replace('task-', '')
            task_params = dict(config[section])
            errors = validate_task(task_params)
            if errors:
                print("Some errors for task %s are found:" % task_name)
                [print(" - %s" % err) for err in errors]
                sys.exit(1)

            settings['TASKS'][task_name] = task_params
        else:
            raise exceptions.UnknownConfigSectionException("Unknown section: %s" % section)

    from gitbarry.utils import shortcuts
    for action, path in FINISH_ACTIONS.items():
        try:
            module = shortcuts.import_from_str(path)
        except ImportError:
            print("Cant import action %s from %s" % (action, path))
            sys.exit(3)
        settings['FINISH_ACTIONS'][action] = module
    return settings

