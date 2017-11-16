"""
Define Global Config module
"""
import configparser
import os


class ConfigWrapper:
    """
    Wrap python default config parser library.
    Load config from system path first then local path.
    overwrite sequence is
    local dir > home dir > $(MIOYING_APPLICATION) > /etc/mioying
    """
    def __init__(self, file_name='application.ini'):
        self._config = configparser.ConfigParser()
        for loc in "/etc/mioying", os.environ.get("MIOYING_APPLICATION"), os.path.expanduser("~"), os.curdir:
            try:
                print("try load config file from %s" % os.path.join(loc, file_name))
                self._config.read(os.path.join(loc, file_name))
            except TypeError:
                pass

    def get_config(self):
        """
        Get config object from class instance
        :return: python configparser object
        """
        return self._config


_CONFIG = ConfigWrapper()
"""
Config Singleton
"""


def get_config():
    """
    Get Config Object for the project
    :return:
    """
    return _CONFIG.get_config()
