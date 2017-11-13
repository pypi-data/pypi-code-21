import os
import os.path as op
import re

from .error import CommandError


POZETRON_DIR_ENV_VAR = 'POZETRON_DIR'
POZETRON_DEFAULT_DIR = '~/.pozetron'


def _get_pozetron_dir():
    path = os.getenv(POZETRON_DIR_ENV_VAR)
    if path:
        path = op.abspath(op.expanduser(path))
    else:
        path = op.expanduser(POZETRON_DEFAULT_DIR)
    return path


def get_logs_dir():
    path = op.join(_get_pozetron_dir(), 'logs')
    return path


def get_tags_filename():
    return op.join(_get_pozetron_dir(), 'tags')


def read_key():
    """
    Returns (key_id, secret_bytes).

    Can use alternative location from POZETRON_DIR.
    """
    path = _get_pozetron_dir()
    config_file_location = op.join(path, 'id_pozetron')
    if not op.isdir(path):
        raise CommandError('Config file not found, configuration directory does not exist: {}'
                           .format(path))
    errors = []
    if not op.isfile(config_file_location):
        errors.append('Config file not found: {}'.format(config_file_location))
    else:
        # Read and validate config
        with open(config_file_location) as file:
            line = file.read()
            match = re.match(r'^(\w+)\s+(\w+).*$', line)
            if not match:
                errors.append('Invalid config file: {}'.format(config_file_location))
            else:
                key_id, secret = match.group(1, 2)
    if errors:
        raise CommandError('\n'.join(errors))
    return key_id, secret
