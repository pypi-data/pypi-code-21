import configlib


def save_version(config, major, minor, patch):
    with config:
        config.version = '%d.%d.%d' % (major, minor, patch)


class ManConfig(configlib.Config):
    """
    This configuration is used for each lib to describe it.
    """

    __config_path__ = './manconfig.json'  # always in the directory where invocated

    libname = ''
    github_username = ''
    fullname = ''
    email = ''
    pypi_username = ''
    version = '0.0.0'
    description = ''

    package_data = dict()
    __package_data_type__ = configlib.Python(dict)

    data_files = []
    __data_files_type__ = configlib.Python(list)

    packages = []
    __packages_type__ = configlib.Python(list)

    dependancies = []
    __dependancies_type__ = configlib.Python(list)
