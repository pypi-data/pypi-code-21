import inspect
import logging
import os

import appdirs
import pkg_resources
import yaml

from .meta import TypeStructure
# from .containers import Structure, Dict, List
from . import containers, fields


class ConfigFile(object):
    def __init__(self, config_path, config, appname=None):
        """
        Config file container.
        :param str config_path: path to file for storage. Either absolute
                                 or relative. If relative, appname is required
                                 to determine user config folder for platform
        :param Structure config: top level config item
        :param str appname: When using relative path fon config_file,
                             appname is required for user config dir
        """
        self.write_enabled = False
        self.config_path = str(config_path)
        # convert passed in config to a registered instance
        self.config = self.register_structure(config)
        conftype = config if config.__class__ is TypeStructure else config.__class__
        assert isinstance(self.config, conftype)
        log = logging.getLogger("Config")

        if not os.path.isabs(self.config_path):
            if not appname:
                try:
                    mainpkg = __import__('__main__').__package__.split('.')[0]
                    appname = pkg_resources.get_distribution(mainpkg).project_name
                except (AttributeError, IndexError):
                    raise ValueError("Must provide appname for relative config file path")
            appdir = appdirs.user_data_dir(appname=appname)
            if not os.path.exists(appdir):
                try:
                    os.makedirs(appdir)
                except:
                    pass
            self.config_path = os.path.join(appdir, self.config_path)

        # Startup
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as configfile:
                saved_config = yaml.load(configfile).__getstate__()
                self.config.__setstate__(saved_config)
                log.info("Loaded config from %s" % self.config_path)

        self.write_enabled = True

        # Ensure the config file exists for new installations.
        if not os.path.exists(self.config_path):
            self.write_yaml()
            log.info("Initialised new config file at %s" % self.config_path)

    def write_yaml(self):
        if self.write_enabled:
            try:
                os.makedirs(os.path.dirname(self.config_path))
            except OSError:
                pass
            with open(self.config_path, 'w') as configfile:
                yaml.dump(self.config, configfile,
                          default_flow_style=False, Dumper=NoAliasDumper)

    def register_structure(self, structure):
        """
        This will attach this config files' writer to the structure
        :param Structure structure: key to register
        :returns: structure as passed in
        """

        def attach(_structure):
            if inspect.isclass(_structure) and issubclass(_structure, containers.Structure):
                _structure = _structure()
            if isinstance(_structure, containers.Structure):
                _structure.__reg_configfile__(self)

            return _structure

        def register_val(_val):
            if isinstance(_val, containers.Dict):
                _val.__reg_configfile__(self)
            elif isinstance(_val, containers.List):
                _val.__reg_configfile__(self)

            if isinstance(_val, dict):
                _val = containers.Dict(_val)
                for k, v in _val.items():
                    _val[k] = attach(v)
                _val.__reg_configfile__(self)
            elif isinstance(_val, (list, set, tuple)):
                _val = containers.List((attach(v) for v in _val))
                _val.__reg_configfile__(self)

            else:
                _val = attach(_val)
            return _val

        structure = register_val(structure)

        if isinstance(structure, containers.Structure):
            for key, val in structure:
                val = register_val(val)
                structure[key] = val
                if isinstance(val, fields.Deprecated):
                    continue

        return structure


def list_rep(dumper, data):
    """
    Ensure pyyaml treats our list as a regular list
    """
    return dumper.represent_list(list(data))


def dict_rep(dumper, data):
    """
    Ensure pyyaml treats our list as a regular list
    """
    return dumper.represent_dict(dict(data))


class NoAliasDumper(yaml.dumper.Dumper):
    """
    Disable alias when writing yaml as these make it harder to
    manually read/modify the config file
    """

    def ignore_aliases(self, data):
        return True


yaml.add_representer(containers.List, list_rep)

yaml.add_representer(containers.Dict, dict_rep)


