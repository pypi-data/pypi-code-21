""":mod:`config` module contains configuration functions and classes for :mod:`latest` package.

:mod:`latest` is configurable both programmatically and through a configuration file.

Configurations are contained in a :class:`_Config` object. Constructor (:code:`__init__` method) of this class
accepts the optional keyword argument :code:`config_file` to specify the location of the configuration file.
If no configuration file is specified, defaults are set in code.
A default configuration object (:code:`config`) is defined in this module and can be imported to be used elsewhere.
I suggest an import statement like

.. code::

    from latest.config import config as Config

so that you can think of it as a class with many static attributes and methods.
To create an alternate configuration object you can use the public function :code:`create_config(config_file=None)`.

Configuration file is found by default (:code:`config` looks for this location)
in :code:`~/.latest/latest.cfg` but one can use his own configuration files.
The formatting of a configuration file must be :code:`ini` format.

Useful sections of a configuration file are:

    * general
    * lang

The section *lang* of a configuration file is where one can define its own syntax.
Available options in `lang` section are:

    * `pyexpr_entry`: the regex indicating the start of a python expression block.
    * `pyexpr_exit`: the regex indicating the end of a python expression block.
    * `env_entry`: the regex indicating the start of a `latest` environment.
    * `env_exit`: the regex indicating the end of a `latest` environment.

"""

import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import latest
from .util import path, getopt


_BASE_DIR = path('~/.' + latest.__project__ + '/')
_CONFIG_FILE = os.path.join(_BASE_DIR, latest.__project__ + 'cfg')
_TEMPLATES_DIR = os.path.join(_BASE_DIR, 'templates/')


class _Config(object):

    _OPTIONS = (
        # section, key, default
        ('general', 'templates_dir', _TEMPLATES_DIR),
        ('general', 'join', str()),
        ('lang', 'pyexpr_entry', r'\{\$'),
        ('lang', 'pyexpr_exit', r'\$\}'),
        ('lang', 'opts_entry', r'\['),
        ('lang', 'opts_exit', r'\]'),
        ('lang', 'str_pyexpr_entry', r'\\latest'),
        ('lang', 'str_pyexpr_exit', None),
        ('lang', 'env_entry', r'\\begin\{latest\}'),
        ('lang', 'env_exit', r'\\end\{latest\}')
    )

    def __init__(self, config_file=None):
        if config_file:
            self.read(config_file)
        else:
            self.set_defaults()

    def set_defaults(self):
        for section, key, default in self._OPTIONS:
            setattr(self, key, default)

    def read(self, filename):

        config_file = path(filename)
        if not hasattr(self, 'config_files'):
            self.config_files = list()
        self.config_files.append(config_file)

        parser = configparser.RawConfigParser()
        parser.read(config_file)
        for section, key, default in self._OPTIONS:
            value = getopt(parser, section, key, default)
            setattr(self, key, value)


def create_config(config_file=None):
    return _Config(config_file)

config = _Config(config_file=_CONFIG_FILE)
