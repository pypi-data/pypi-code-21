import os
import logging

from the_conf import files, command_line, node, interractive

logger = logging.getLogger(__name__)
DEFAULT_ORDER = 'cmd', 'files', 'env'
DEFAULT_CONFIG_FILE_CMD_LINE = '-C', '--config'
DEFAULT_CONFIG_FILE_ENVIRON = ('CONFIG_FILE',)


class TheConf(node.ConfNode):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, *metaconfs, prompt_values=False,
                 cmd_line_opts=None, environ=None):
        self._source_order = DEFAULT_ORDER
        self._config_files = None
        self._config_file_cmd_line = DEFAULT_CONFIG_FILE_CMD_LINE
        self._config_file_environ = DEFAULT_CONFIG_FILE_ENVIRON
        self._main_conf_file = None
        self._cmd_line_opts = cmd_line_opts
        self._environ = environ
        self._prompt_values = prompt_values

        super().__init__()
        for mc in metaconfs:
            if isinstance(mc, str):
                _, _, mc = next(files.read(mc))
            if self._source_order is DEFAULT_ORDER:
                self._source_order = mc.get('source_order', DEFAULT_ORDER)
            if self._config_file_cmd_line is DEFAULT_CONFIG_FILE_CMD_LINE:
                self._config_file_cmd_line = mc.get('config_file_cmd_line',
                        DEFAULT_CONFIG_FILE_CMD_LINE)
            if self._config_file_cmd_line is DEFAULT_CONFIG_FILE_ENVIRON:
                self._config_file_environ = mc.get('config_file_environ',
                        DEFAULT_CONFIG_FILE_ENVIRON)
            if self._config_files is None:
                self._config_files = mc.get('config_files', None)

            self._load_parameters(*mc['parameters'])
        self.load()

    def _load_files(self):
        if self._config_files is None:
            return
        for conf_file, _, config in files.read(*self._config_files):
            paths = (path for path, _, _ in self._get_path_val_param())
            for path, value in files.extract_values(paths, config, conf_file):
                self._set_to_path(path, value)

    def _load_cmd(self, opts=None):
        gen = command_line.yield_values_from_cmd(
                list(self._get_path_val_param()), self._cmd_line_opts,
                self._config_file_cmd_line)
        config_file = next(gen)
        if config_file:
            self._config_files.insert(0, config_file)

        for path, value in gen:
            self._set_to_path(path, value)

    def _load_env(self, environ=None):
        if environ is None:
            environ = os.environ
        for config_env_key in self._config_file_environ:
            if config_env_key in environ:
                self._config_files.insert(0, environ[config_env_key])
        for path, _, _ in self._get_path_val_param():
            env_key = '_'.join(map(str.upper, path))
            if env_key in environ:
                self._set_to_path(path, environ[env_key])

    def load(self):
        for order in self._source_order:
            if order == 'files':
                self._load_files()
            elif order == 'cmd':
                self._load_cmd(self._cmd_line_opts)
            elif order == 'env':
                self._load_env(self._environ)
            else:
                raise Exception('unknown order %r')

        if self._prompt_values:
            self.prompt_values(False, False, False, False)

        for path, value, param in self._get_path_val_param():
            if value is node.NoValue and param.get('required'):
                raise ValueError('loading finished and %r is not set'
                        % '.'.join(path))

    def _extract_config(self):
        config = {}
        for paths, value, param in self._get_path_val_param():
            if value is node.NoValue:
                continue
            if 'default' in param and value == param['default']:
                continue
            curr_config = config
            for path in paths[:-1]:
                curr_config[path] = {}
                curr_config = curr_config[path]
            curr_config[paths[-1]] = value
        return config

    def write(self, config_file=None):
        if config_file is None and not self._config_files:
            raise ValueError('no config file to write in')

        files.write(self._extract_config(),
                config_file or self._config_files[0])

    def prompt_values(self, only_empty=True, only_no_default=True,
            only_required=True, only_w_help=True):
        for path, value, param in self._get_path_val_param():
            if only_w_help and not param.get('help_txt'):
                continue
            if only_required and not param.get('required'):
                continue
            if only_no_default and not param.get('default'):
                continue
            if only_empty and value is not node.NoValue:
                continue
            if param.get('type') is bool:
                self._set_to_path(path, interractive.ask_bool(
                    param.get('help_txt', '.'.join(path)),
                    default=param.get('default'),
                    required=param.get('required')))
            else:
                self._set_to_path(path, interractive.ask(
                    param.get('help_txt', '.'.join(path)),
                    choices=param.get('among'), default=param.get('default'),
                    required=param.get('required'), cast=param.get('type')))
