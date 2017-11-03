import configparser
import os
from .validator import validate_settings
from .convert import config2settings

__all__ = ['settings', ]

config_name = 'gitbarry.ini'

config = configparser.ConfigParser()
try:
    if os.path.isfile(config_name):
        config.read(config_name)
        print("Using %s" % os.path.abspath(config_name))
except IOError:
    print("%s does not exists. Using default." % config_name)
    config['task-feature'] = {
        "branch-from": "master",
        "finish-branch-to": "master",
        "finish-action": "pull-request",
        "pull-request-method": "POST",
        "pull-request-url": "http://ya.ru",
    }

    config['task-hotfix'] = {
        "branch-from": "master",
        "finish-branch-to": "master",
        "finish-action": "merge",
    }

settings = config2settings(config)
validation_errors = validate_settings(settings)
