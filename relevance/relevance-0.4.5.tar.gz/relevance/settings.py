"""
This module provides the interfaces for loading settings from configuration files
into useable objects.
"""

import os
import typing
import anyconfig


class Settings(dict):
    """
    This class represents a settings configuration.

    Although it can be instantiated manually, it is typically created using a
    :class:`SettingsFactory` instance.
    """
    def __init__(self, name: str, data: typing.Iterable = '') -> None:
        """
        :param name: the name to give this settings subset.
        :param data: the iterable to import as data.
        """
        super().__init__(data)
        self.name = name

    def __getitem__(self, key: str) -> object:
        """
        Get a settings item in dictionary fashion.

        This method is mostly used if no validation of the data type is required.
        If validation is required, use the :meth:`Settings.get_type` method instead.

        :return: the found setting object. If the result is a :class:`dict`, it will
        be automatically converted into a :class:`Settings` object.
        :raises: :class:`RequiredSettingError`: if the setting is missing.
        """
        name = '{0}/{1}'.format(self.name, key)

        try:
            item = super().__getitem__(key)
        except KeyError as ex:
            raise RequiredSettingError(str(ex))

        if not isinstance(item, dict):
            return item

        return Settings(name, item)

    def get_type(self, key: str, data_type: type) -> object:
        """
        Get a setting and validate its type.

        :param key: the setting key to retrieve.
        :param data_type: a data type to validate against, such as :class:`str`.
        :return: the found setting object. If the result is a :class:`dict`, it will
            be automatically converted into a :class:`Settings` object.
        :raises: :class:`InvalidSettingTypeError`: if the data type is invalid.
        """
        name = '{0}/{1}'.format(self.name, key)
        item = self[key]

        if not isinstance(item, data_type):
            raise InvalidSettingTypeError(key, data_type)

        if not isinstance(item, dict):
            return item

        return Settings(name, item)

    def get(self, key: str, default: object = None, data_type: type = None) -> object:
        """
        Get an optional settings and validate its type.

        If the requested settings is not found, the `default` value is returned.

        :param data_type: an optional data type to validate against, e.g.: :class:`str`.
        :return: the found setting object. If the result is a :class:`dict`, it will
            be automatically converted into a :class:`Settings` object.
        :raises: :class:`InvalidSettingTypeError`: if the data type is invalid.
        """
        name = '{0}/{1}'.format(self.name, key)
        item = super().get(key, default)

        if data_type is not None and not isinstance(item, data_type) and default is not None:
            raise InvalidSettingTypeError(key, data_type)

        if not isinstance(item, dict):
            return item

        return Settings(name, item)

    def resolve(self, path: str) -> object:
        """
        Resolve a nested dictionary key path.

        When manipulating settings objects with multiple levels, this method allows
        to resolve a sub-object quickly, using slashes as separators.

        :param path: the path to resolve.
        :return: the resolved value.
        """
        parts = path.split('/')
        ref: typing.Any = self
        for part in parts:
            ref = ref[part]
        return ref

    def first_item(self, data_type: type = None) -> tuple:
        """
        Get the first item.

        :param data_type: an optional data type to validate against.
        :return: a tuple containing the key and the value of the first item
            in the settings object.
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

    def items(self):
        """
        Implementation of :meth:`dict.__iter__`.
        """
        for key, value in super().items():
            if not isinstance(value, dict):
                yield (key, value)
            else:
                yield (key, Settings(key, value))


class SettingsFactory(object):  # pylint: disable=too-few-public-methods
    """
    This class allows to load one or multiple files, based on environment, in
    specific directories as settings objects.
    """
    def __init__(self, dirs: list, default_env: str = 'devel', env: str = None) -> None:
        """
        :param dirs: a list of directories to lookup, in reverse priority order
            (the last one overrides the first one).
        :param default_env: the default environment to use if none is set. The
            factory uses the `PYTHON_ENV` environment variable to determine the
            name of the environment.
        :param env: the environment to enforce, whether it is set or not.
        """
        self.dirs = dirs
        self.env = env if env is not None else os.getenv('PYTHON_ENV', default_env)

    def load(self, pattern: str) -> Settings:
        """
        Load a settings object from configuration files.

        :param pattern: the string pattern to match, i.e.: the base name of the
            configuration filename. Per example, given a `pattern` of `foo`, and
            an environment name of `bar`, the following files will be attempted in
            this order: `foo.json`, `foo.yml`, `foo.bar.json`, `foo.bar.yml`.
        :return: a settings object.
        """
        filenames: typing.List[str] = []

        for dirname in self.dirs:
            filenames += [
                '{0}/{1}.json'.format(dirname, pattern),
                '{0}/{1}.yml'.format(dirname, pattern),
                '{0}/{1}.{2}.json'.format(dirname, pattern, self.env),
                '{0}/{1}.{2}.yml'.format(dirname, pattern, self.env),
            ]

        data = anyconfig.load(filenames, ignore_missing=True)
        return Settings(pattern, data)


class RequiredSettingError(KeyError):
    """
    This exception is raised when attempting to retrieve a settings by its key
    and the key does not exist in the settings object.
    """
    pass


class InvalidSettingTypeError(TypeError):
    """
    This exception is raised when retrieving a setting, but the returned value
    does not have the expected data type.
    """
    def __init__(self, key: str, data_type: type) -> None:
        """
        :param key: the name of the setting that was retrieved.
        :param data_type: the expected data type.
        """
        super().__init__('setting {0} expected to be a {1}'.format(
            key, data_type,
        ))
        self.key = key
        self.data_type = data_type


class InvalidSettingValueError(ValueError):
    """
    This exception is raised when the value of a setting is has an unexpected
    value.
    """
    pass
