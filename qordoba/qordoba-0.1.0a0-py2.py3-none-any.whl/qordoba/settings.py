from __future__ import unicode_literals, print_function

import logging
import os
import yaml
import yaml.parser

log = logging.getLogger('qordoba')

DEFAULT_SETTING_PATH = os.path.abspath(os.path.join(os.getcwd(), '.qordoba.yml'))

SETTING_PATHS = (
    os.environ.get('QORDOBA_CONFIG', ''),
    DEFAULT_SETTING_PATH,
    os.path.abspath(os.path.join(os.path.expanduser('~'), '.qordoba.yml'))
)


class SettingsError(Exception):
    """
    Settings error
    """


class SettingsValidationError(SettingsError):
    """
    Settings validation error
    """

class PatternNotFound(SettingsError):
    pass


class SettingsDict(dict):
    def __init__(self, path=DEFAULT_SETTING_PATH, validate=True, **kwargs):
        super(SettingsDict, self).__init__()
        self.path = path

        for k, v in kwargs.items():
            self[k.lower()] = v

        # if validate:
        #     self.validate()

    def validate(self, keys=('project_id', 'access_token')):
        for key in keys:
            try:
                v = self[key]
                if v is None:
                    raise KeyError
            except KeyError:
                raise SettingsValidationError(
                    """{} param is required. Please provide it by argument or in config file.""".format(key))


def load_settings_from_file(path):
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
            if not config or not config.get('qordoba', None):
                log.warning('Could not parse config file: {}'.format(path))
                return {}

            return config['qordoba']

    except (yaml.parser.ParserError, KeyError):
        log.debug('Could not parse config file: {}'.format(path))
        raise SettingsError('Could not parse config file: {}'.format(path))
    except IOError:
        raise SettingsError('Could not open config file: {}'.format(path))


def dump_settings(path, data):
    data = {
        str('qordoba'): data.copy()
    }
    with open(path, 'w') as f:
        yaml.safe_dump(data, f, default_flow_style=False)

    log.debug('Created config file: {}\n{}'.format(path, data))


def load_settings(**kwargs):

    settings = None
    loaded = False
    for path in SETTING_PATHS:
        try:
            data = load_settings_from_file(path)
        except SettingsError:
            pass
        else:
            data.update({k: v for k, v in kwargs.items() if v is not None})
            settings = SettingsDict(path=path, **data)
            loaded = True
            break

    if settings is None:
        settings = SettingsDict(**kwargs)

    return settings, loaded


NOTDEFINED = object()


def save_settings(config):
    config.validate()

    dump_settings(config.path, config)

    log.info('Config `{}` successfully saved.'.format(config.path))

    return config

def get_find_new_pattern(config):
    try:
        return [pattern_row for pattern_row in config['search']['paths']]
    except (KeyError, IndexError):
        raise PatternNotFound('Pattern not found for source files')


def get_find_new_blacklist_pattern(config):
    exclude_list = config['search'].get('exclude', [])
    return [exception_row for exception_row in exclude_list]


def get_push_pattern(config):
    try:
        return config['push']['sources']
    except (KeyError, IndexError):
        raise PatternNotFound('Pattern not found for source files')


def get_pull_pattern(config, default=NOTDEFINED):
    try:
        return config['pull']['targets']
    except (KeyError, IndexError):
        if default is not NOTDEFINED:
            return None
        raise PatternNotFound('Pattern not found for target files')


def get_project_file_formats(config, default=None):
    try:
        return config['file_formats']
    except (KeyError, IndexError):
        return None