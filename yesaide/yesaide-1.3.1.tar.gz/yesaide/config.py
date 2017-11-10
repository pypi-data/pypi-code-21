import importlib.machinery
import importlib.util
import os


class ConfigError(KeyError):
    """Exception thrown when the requested key does not exist."""


class Required(object):
    """Simple placeholder to use in default config to indicate that a
    value has to be given for the config to be "valid"."""


class Config(object):
    """Has a dict-like interface with some handy subtilities regarding
    config management.

    """

    def __init__(self, *, default_config=None, env_prefix=None):
        self.env_prefix = env_prefix

        self.base_values = {}
        self.set_values = {}
        self.required_values = []

        if default_config:
            self.required_values = self.from_object(
                default_config,
                unwrap_required=True,
            )

    def __getitem__(self, name):
        try:
            return self.set_values[name]
        except KeyError:
            pass

        if self.env_prefix:
            try:
                return os.environ[self.env_prefix + name]
            except KeyError:
                pass

        try:
            return self.base_values[name]
        except KeyError:
            raise ConfigError(
                'The requested config value, {}, is not set.'.format(name))

    def __setitem__(self, name, value):
        self.set_values[name] = value

    def get(self, name, default_value=None):
        try:
            return self.__getitem__(name)
        except ConfigError:
            return default_value

    def from_object(self, obj, *, unwrap_required=False):
        rv = []

        for key in dir(obj):
            if key.isupper():
                v = getattr(obj, key)

                if unwrap_required and isinstance(v, Required):
                    rv.append(key)
                    v = None

                self.base_values[key] = v

        if unwrap_required:
            return rv

    def from_pyfile(self, filename):
        spec = importlib.machinery.ModuleSpec(
            'config',
            importlib.machinery.SourceFileLoader('config', filename),
            origin=filename,
        )
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        self.from_object(config)

    def is_valid(self):
        for key in self.required_values:
            if self.get(key, None) is None:
                return False
        return True

    def missing_values(self):
        rv = []
        for key in self.required_values:
            if self.get(key, None) is None:
                rv.append(key)
        return rv
