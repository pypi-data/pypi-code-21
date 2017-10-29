#!/usr/bin/env python
"""General configuration and command line option management.

One of the 'patterns' that regularly occurs for me, is the need to provide
program configuration options using a variety of methods. In order of
precedence (later methods over-ride earlier methods) these are:

    1. Setting default values for when no other method has been used.
    2. Setting config values using multiple configuration files.
    3. Setting config values using command line options.
    4. Setting config values programmatically.
"""

tx = lambda x: x


class ConfigFile(object):
    """
    Class to store values set in a config file.
    """

    def __init__(self, defaults=None):
        self.__dict__["_isset"] = {}
        if defaults:
            for (attr, val) in defaults.items():
                self.__dict__[attr] = val

    def __setattr__(self, name, value):
        self._isset[name] = True
        self.__dict__[name] = value


class ConfigManager(object):
    """
    Multi-source configuration manager.

    This class provides a wrapping around configuration/options information
    from multiple sources:

    1. Explicitly (programmatically) set values.
    2. Command line options.
    3. Initialisation file(s).
    4. Default (programmatically set) values.

    The above order defines the override precedence; an initialisation file can
    override the default value, which can be overridden by a command line
    option, etc.

    Note: The last config file added takes precedence over other config files
    """

    def __init__(self):
        """Initialisation of the config manager"""
        self.reset()

    def reset(self):
        """Reset the config manager"""
        self._default_values = {}
        self._config_files = []
        self._command_line_manager = None
        self._explicitly_set_values = {}

    def set_option(self, name, value):
        """
        Explicitly set a config item, this will override any other config
        value source
        :param name: The name of the config item
        :param value: The value to assign
        :return: None
        """
        self._explicitly_set_values[name] = value

    def set_default_for_option(self, name, value):
        """
        Set the default for a config item, this value will only be used if
        no other method has been used to assign a value
        :param name: The name of the config item
        :param value: The value to assign
        :return: None
        """
        self._default_values[name] = value

    def set_command_line_option_manager(self, manager):
        """
        Set the command line options manager
        :param manager: The command line option manager, assumed to be a
          ParserManager from Execution
        :return: None
        """
        self._command_line_manager = manager

    def set_config_file_options(self, config_file_path, config_file):
        """
        Set the config file options
        :param config_file_path: The path to the config file
        :param config_file: A ConfigFile instance
        :return: None
        """
        self._config_files.append((config_file_path, config_file))

    def has_option(self, name):
        """
        Check if the ConfigManager knows about a certain option
        :param name: The name of the option
        :return: Boolean does the ConfigManager know about the option
        """
        for dict in self._default_values:
            if name in dict:
                return True

        for dict in self._explicitly_set_values:
            if name in dict:
                return True

        for _, config_file in self._config_files:
            if config_file._isset.get(name, None):
                return True

        if self._command_line_manager is not None and self._command_line_manager.has_arg(name):
            return True

        return False

    def get_option_value(self, name, default=None):
        """
        Get the stored value for a particular option from the most relevant
        source

        :param name: The name of the option
        :param default: A default to use if it can't be found
        :return: A the value of the default
        """
        if name in self._explicitly_set_values:
            return self._explicitly_set_values[name]

        if self._command_line_manager is not None and self._command_line_manager.has_arg(name):
            return self._command_line_manager.get_arg_value(name)

        # Note reversed so that the last config file added takes precedence
        for _, values in reversed(self._config_files):
            if values._isset.get(name, None):
                return getattr(values, name)

        if name in self._default_values:
            return self._default_values[name]

        return default


config_manager = ConfigManager()

#: Option sets identified by name.
_configs = {}


def _getConfig(name):
    if name not in _configs:
        _configs[name] = ConfigManager()
    return _configs[name]


class Options(object):
    def __init__(self, name):
        self.__dict__["_name"] = name
        self.__dict__["_optionsInstance"] = _getConfig(name)

    def __getattr__(self, name):
        return getattr(self._optionsInstance, name)
