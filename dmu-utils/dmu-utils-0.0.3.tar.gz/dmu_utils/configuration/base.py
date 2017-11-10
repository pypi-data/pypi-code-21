import os
import copy
from operator import attrgetter

from objdict import ObjDict
import yaml

from dmu_utils.pkg_resources import get_package_file_content
from dmu_utils.collections import deep_update
from dmu_utils.misc import identity_func


def to_env_var_name(name):
    return name.replace('.', '_').upper()


def read_config(filepath, module_name=None):
    if module_name:
        config = yaml.load(get_package_file_content(module_name, filepath))
    else:
        with open(filepath, 'r') as f:
            config = yaml.load(f)

    if config is None:
        config = {}

    if not isinstance(config, dict):
        raise ValueError('Top level object of configuration file must be a dictionary')

    return ObjDict(config)


class Configuration(object):

    def __init__(self, default_config_module_name, default_config_filepath='default.yaml',
                 local_config_env_var=None, local_config_default_path=None,
                 with_env_override=True, with_commandline_override=True):

        if with_commandline_override:
            raise NotImplementedError('Command line override is not implemented yet')

        self.default_config_module_name = default_config_module_name
        self.default_config_filepath = default_config_filepath

        self.local_config_env_var = local_config_env_var
        self.local_config_default_path = local_config_default_path

        self.with_env_override = with_env_override
        self.with_commandline_override = with_commandline_override

        self._default_config_object = None
        self._config_object = None

    @property
    def default_config_object(self):
        if self._default_config_object is None:
            self._default_config_object = read_config(self.default_config_filepath,
                                                      self.default_config_module_name)

        return self._default_config_object

    @property
    def config_object(self):
        if self._config_object is None:
            config_object = copy.deepcopy(self.default_config_object)

            local_config_path = (os.getenv(self.local_config_env_var) or
                                 self.local_config_default_path)
            deep_update(config_object, read_config(local_config_path))

            self._config_object = config_object

        return self._config_object

    def get(self, name):
        if self.with_commandline_override:
            raise NotImplementedError('Command line override is not implemented yet')

        if self.with_env_override:
            env_var_value = os.getenv(to_env_var_name(name))
            if env_var_value is not None:
                try:
                    default_value = attrgetter(name)(self.default_config_object)
                except AttributeError:
                    coercion_func = identity_func
                else:
                    default_type = type(default_value)
                    if issubclass(default_type, bool):
                        # TODO(dmu) HIGH: Implement bool coercion
                        raise NotImplementedError('bool coercion is not implemented yet')
                    coercion_func = default_type

                return coercion_func(env_var_value)

        return attrgetter(name)(self.config_object)
