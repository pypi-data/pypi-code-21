"""
Relevance settings module.

This module provides the interfaces for loading settings from configuration files
into useful objects.
"""

import os
import typing
import anyconfig


class RequiredSettingError(KeyError):
    """
    Exception raised when a required setting is missing.
    """
    pass


class InvalidSettingTypeError(TypeError):
    """
    Exception raised when a setting has invalid type.
    """
    def __init__(self, key: str, data_type: type):
        """
        Initialize the exception.

        :param key: the name of the setting.
        :param data_type: the expected data type.
        """
        super().__init__('setting {0} expected to be a {1}'.format(
            key, data_type,
        ))
        self.key = key
        self.data_type = data_type


class InvalidSettingValueError(ValueError):
    """
    Exception raised when a setting has invalid value.
    """
    pass


class Settings(dict):
    """
    Settings class.

    This class represents a settings configuration.
    """
    def __init__(self, name: str, data: typing.Iterable=''):
        """
        Initialize the settings.

        :param name: the name to give this settings subset.
        :param data: the iterable to import as data.
        """
        super().__init__(data)
        self.name = name

    def __getitem__(self, key: str) -> object:
        """
        Overload dictionary method.

        :raises: RequiredSettingError: if the setting is missing.
        """
        name = '{0}/{1}'.format(self.name, key)

        try:
            item = super().__getitem__(key)
        except KeyError as e:
            raise RequiredSettingError(str(e))

        if not isinstance(item, dict):
            return item

        return Settings(name, item)

    def first_item(self, data_type: type=None) -> tuple:
        """
        Get the first item in the object.

        :param data_type: an optional data type to validate against.
        :raises: InvalidSettingTypeError: if the data type is invalid.
        """
        try:
            key, value = list(self.keys())[0], list(self.values())[0]
        except TypeError:
            raise RequiredSettingError()

        if data_type is not None and not isinstance(value, data_type):
            raise InvalidSettingTypeError(key, data_type)

        if not isinstance(value, dict):
            return (key, value)

        return (key, Settings(key, value))

    def items(self) -> typing.Iterable:
        """
        Overload dictionary method.
        """
        for x, y in super().items():
            if not isinstance(y, dict):
                yield (x, y)
            else:
                yield (x, Settings(x, y))

    def get(self, key: str, default: object=None, data_type: type=None) -> object:
        """
        Overload dictionary method.

        :param data_type: an optional data type to validate against.
        :raises: InvalidSettingTypeError: if the data type is invalid.
        """
        name = '{0}/{1}'.format(self.name, key)
        item = super().get(key, default)

        if data_type is not None and not isinstance(item, data_type) and default is not None:
            raise InvalidSettingTypeError(key, data_type)

        if not isinstance(item, dict):
            return item

        return Settings(name, item)

    def get_type(self, key: str, data_type: type) -> object:
        """
        Get a setting and validate its type.

        :param key: the setting key to retrieve.
        :param data_type: an optional data type to validate against.
        :raises: InvalidSettingTypeError: if the data type is invalid.
        """
        name = '{0}/{1}'.format(self.name, key)
        item = self[key]

        if not isinstance(item, data_type):
            raise InvalidSettingTypeError(key, data_type)

        if not isinstance(item, dict):
            return item

        return Settings(name, item)

    def resolve(self, path: str) -> object:
        """
        Resolve a nested dictionary key path.

        :param path: the path to resolve.
        :returns: the resolved value.
        """
        parts = path.split('/')
        ref = self
        for x in parts:
            ref = ref[x]
        return ref


class SettingsFactory(object):
    """
    Settings factory class.

    This class allows to load one or multiple files, based on environment, in
    specific directories as settings objects.
    """
    def __init__(self, dirs: list, default_env: str='devel', env: str=None):
        """
        Initialize the factory.

        :param dirs: a list of directories to lookup, in reverse priority order.
        :param default_env: the default environment to use if none is set.
        :param env: the environment to enforce, whether it is set or not.
        """
        self.dirs = dirs
        self.env = env if env is not None else os.getenv('PYTHON_ENV', default_env)

    def load(self, pattern: str) -> Settings:
        """
        Load a settings object.

        :param pattern: the string pattern to match, i.e.: the base name of the
        configuration filename.
        :returns: a settings object.
        """
        filenames = []

        for dirname in self.dirs:
            filenames += [
                '{0}/{1}.json'.format(dirname, pattern),
                '{0}/{1}.yml'.format(dirname, pattern),
                '{0}/{1}.{2}.json'.format(dirname, pattern, self.env),
                '{0}/{1}.{2}.yml'.format(dirname, pattern, self.env),
            ]

        data = anyconfig.load(filenames, ignore_missing=True)

        return Settings(pattern, data)
