import logging

from the_conf import files, command_line, node

logger = logging.getLogger(__name__)
DEFAULT_ORDER = 'cmd', 'files', 'env'


class TheConf(node.ConfNode):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, *metaconfs, cmd_line_opts=None):
        self._source_order = DEFAULT_ORDER
        self._config_files = None
        self._main_conf_file = None
        self._cmd_line_opts = cmd_line_opts

        super().__init__()
        for mc in metaconfs:
            if isinstance(mc, str):
                _, _, mc = next(files.read(mc))
            if self._source_order is DEFAULT_ORDER:
                self._source_order = mc.get('source_order', DEFAULT_ORDER)
            if self._config_files is None:
                self._config_files = mc.get('config_files', None)

            self._load_parameters(*mc['parameters'])
        self.load()

    def load_files(self):
        if self._config_files is None:
            return
        for config_file, _, config in files.read(*self._config_files):
            paths = self._get_all_parameters_path()
            for path, value in files.extract_values(
                    paths, config, config_file):
                self._set_to_path(path, value)

    def load_cmd(self, opts=None):
        parser = command_line.get_parser(self)
        cmd_line_args = parser.parse_args(opts)
        config_file = getattr(cmd_line_args, command_line.CONFIG_OPT_DEST)
        if config_file:
            self._config_files.insert(0, config_file)
        for path in self._get_all_parameters_path():
            value = getattr(cmd_line_args, command_line.path_to_dest(path))
            if value is not None:
                self._set_to_path(path, value)

    def load_env(self):
        pass

    def load(self):
        for order in self._source_order:
            if order == 'files':
                self.load_files()
            elif order == 'cmd':
                self.load_cmd(self._cmd_line_opts)
            elif order == 'env':
                self.load_env()
            else:
                raise Exception('unknown order %r')
