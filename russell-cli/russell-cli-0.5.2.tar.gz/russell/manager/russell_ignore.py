import os

from russell.constants import DEFAULT_FLOYD_IGNORE_LIST
from russell.log import logger as russell_logger


class RussellIgnoreManager(object):
    """
    Manages .russellignore file in the current directory
    """

    CONFIG_FILE_PATH = os.path.join(os.getcwd() + "/.russellignore")

    @classmethod
    def init(cls):
        if os.path.isfile(cls.CONFIG_FILE_PATH):
            russell_logger.debug("russell ignore file already present at {}".format(cls.CONFIG_FILE_PATH))
            return

        russell_logger.debug("Setting default russell ignore in the file {}".format(cls.CONFIG_FILE_PATH))

        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(DEFAULT_FLOYD_IGNORE_LIST)

    @classmethod
    def get_list(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return []

        ignore_dirs = []
        with open(cls.CONFIG_FILE_PATH, "r") as russell_ignore_file:
            for line in russell_ignore_file:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_dirs.append(line)

        return ignore_dirs
