import os

import configlib

class GeneralConfig(configlib.Config):
    """
    This configuration is used when creating new libs with `man create-lib`
    It help to provides defaults.
    """

    __config_path__ = os.path.expanduser('~/generalconfig.json')

    github_username = ''
    fullname = ''
    email = ''
    pypi_username = ''
