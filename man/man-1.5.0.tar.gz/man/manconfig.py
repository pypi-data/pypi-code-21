import re
import configlib


class Version:
    """
    This class describes and manipulate a version number of the form MAJOR.MINOR.PATCH

    When you want to manipulate a version, it is better to do it with a context manager
    and set version.need_revert = False before exiting the context manager so it will
    change the version only if your program had no errors. If you want to do stuff when
    the verision reverts, you can set revert_version to your own function just after
    entering the context manager.
    """

    MAJOR = 0
    MINOR = 1
    PATCH = 2

    def __init__(self, major: int, minor: int, patch: int):
        self.version = [major, minor, patch]
        self.last = None  # type: Version
        self.need_revert = True

    def __str__(self):
        return '%d.%d.%d' % tuple(self.version)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = getattr(self, key.upper())  # type: int

        self.version[key] = value
        for importance in range(key + 1, 3):
            self.version[importance] = 0

    def __getitem__(self, item):
        if isinstance(item, str):
            item = getattr(self, item.upper())

        return self.version[item]

    def __enter__(self):
        self.last = Version(*self.version)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.need_revert:
            self.version = self.last.version[:]
            self.last = None
            self.revert_version()

        self.need_revert = True
        self.revert_version = lambda: 0

    def revert_version(self):
        pass


class VersionType(configlib.ConfigType):

    name = 'version'

    def save(self, value: Version):
        return str(value)

    def is_valid(self, value):
        return isinstance(value, Version)

    def load(self, value: str):
        match = re.match('^v?(\d+)\.(\d+)\.(\d+)$', value)
        if match:
            return Version(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        raise ValueError


class ManConfig(configlib.Config):
    """
    This configuration is used for each lib to describe it.
    """

    __config_path__ = './.manconfig'  # always in the directory where invocated

    libname = ''
    description = ''
    fullname = ''
    email = ''
    github_username = ''
    pypi_username = ''
    keywords = ''

    scripts = []
    __scripts_type__ = configlib.Python(list)


    classifiers = []
    __identyfiers_type__ = configlib.Python(list)

    version = Version(0, 0, 0)
    __version_type__ = VersionType()

    package_data = dict()
    __package_data_type__ = configlib.Python(dict)

    data_files = []
    __data_files_type__ = configlib.Python(list)

    packages = []
    __packages_type__ = configlib.Python(list)

    dependancies = []
    __dependancies_type__ = configlib.Python(list)


__all__ = ['ManConfig']
