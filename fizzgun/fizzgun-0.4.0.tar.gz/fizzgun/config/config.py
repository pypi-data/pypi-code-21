import yaml

from fizzgun.application.service_contexts import FileSystem
from fizzgun.config.defaults import defaults


class Config(object):
    def __init__(self, config_path, file_system: FileSystem):

        self._config = defaults()
        config_file_path = self._get_config_path(config_path, file_system)

        if config_file_path:
            content = file_system.read_file(config_file_path)
            self._config.update(yaml.load(content))

    @property
    def filters(self):
        return self._config['filters']

    @property
    def mitmproxy(self):
        return self._config['mitmproxy']

    @property
    def bubbles(self):
        return self._config['bubbles']

    @property
    def report(self):
        return self._config['report']

    @property
    def stack(self):
        return self._config['stack']

    def _get_config_path(self, user_config_path_option: str or None, file_system: FileSystem):
        if user_config_path_option:
            return user_config_path_option

        return next((path for path in ['fizzgun.yaml', 'fizzgun.yml'] if file_system.is_file(path)), None)

    def __getitem__(self, item):
        return self._config[item]
