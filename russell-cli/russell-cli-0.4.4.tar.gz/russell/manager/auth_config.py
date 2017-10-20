import json
import os

from russell.model.access_token import AccessToken
from russell.log import logger as russell_logger


class AuthConfigManager(object):
    """
    Manages ~/.russellconfig file with access token
    """

    CONFIG_FILE_PATH = os.path.expanduser("~/.russellconfig")

    @classmethod
    def set_access_token(cls, access_token):
        russell_logger.debug("Setting {} in the file {}".format(access_token.to_dict(),
                                                              cls.CONFIG_FILE_PATH))
        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(json.dumps(access_token.to_dict()))

    @classmethod
    def get_access_token(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return None

        with open(cls.CONFIG_FILE_PATH, "r") as config_file:
            access_token_str = config_file.read()
        return AccessToken.from_dict(json.loads(access_token_str))

    @classmethod
    def purge_access_token(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return True

        os.remove(cls.CONFIG_FILE_PATH)
