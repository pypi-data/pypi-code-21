# Copyright (C) 2016-2017,BGI ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

#
import os
import ConfigParser
from os.path import expanduser
import bgionline
from bgionline import logger

UPLOAD_THREADS_NUM = 10
PART_SIZE = 100 * 1024 * 1024
MULTIPART_THRESHOLD = 100 * 1024 * 1024

class BOConfig():
    """
    BGI Online Configuration class.
    """

    # defaults
    staging = False
    host = "app.bgionline.com"
    port = 8081
    protocol = "https"
    username = None
    security_token = "secret"
    current_project_id = None
    current_project_name = None
    current_wd = "/"
    current_path_id = None
    default_config_dir = expanduser("~/.bgionline")
    user_config_dir = None
#    storage_host = None
    sts_token = None
    sts_token_time = 0

    setting_keys = [
        "host", "port", "protocol",
        "username", "security_token",
        "current_project_id", "current_project_name", "current_wd",
        "current_path_id", "default_config_dir", "user_config_dir",
        "storage_host", "sts_token", "sts_token_time"
    ]

    def __init__(self):
        if self.user_config_dir is None:
            self.user_config_dir = self.default_config_dir

        if os.path.exists(self.user_config_dir):
            logger.debug("reading configuration file")
            self.read_config(self.user_config_dir)
        else:
            logger.debug("use system default settings")
        self._sync_global_setting()

    def _sync_global_setting(self):
        # update global setting
        logger.debug("sync bgionline settings")
        bgionline.set_server_info(self.host, self.port, self.protocol)
        # bgionline.set_username(self.username)
        # bgionline.set_auth_token(self.security_token)

    def read_config(self, config_dir):
        self.user_config_dir = config_dir
        config_parser = ConfigParser.ConfigParser()
        try:
            config_parser.read(os.path.join(config_dir, "setting"))
            for k in self.setting_keys:
                setattr(BOConfig, k, config_parser.get("bgionline", k))
        except Exception as e:
            if config_dir != self.default_config_dir and config_dir is not None:
                print "The folder you selected does not have a configuration file,Use default configuration"
            logger.debug(str(e) + "use default configuration")

        # suppress by environment variables
        logger.debug("suppressed by environment variables")

        # if "BGIONLINE_SERVER_HOST" in os.environ:
        #     self.host = os.environ.get("BGIONLINE_SERVER_HOST")
        #
        # if "BGIONLINE_SERVER_PORT" in os.environ:
        #     self.port = os.environ.get("BGIONLINE_SERVER_PORT")
        #
        # if "BGIONLINE_SERVER_PROTOCOL" in os.environ:
        #     self.protocol = os.environ.get("BGIONLINE_SERVER_PROTOCOL")

            # # update setting
            # self._sync_global_setting()

    def save(self, config_dir=None):
        try:
            os.makedirs(self.user_config_dir)
        except OSError as e:
            logger.debug("OS Error:" + str(e))

        config_parser = ConfigParser.ConfigParser()
        config_parser.add_section("bgionline")

        for k in self.setting_keys:
            config_parser.set("bgionline", k, getattr(self, k))
            # print getattr(self, k)
        config_parser.write(open(os.path.join(config_dir or self.user_config_dir, "setting"), "w"))

    def get_user_config(self):
        return os.path.join(self.user_config_dir, "setting")


if __name__ == "__main__":
    config = BOConfig()
    import random

    config.username = random.choice(["user1", ])
    logger.debug(config.host)
    logger.debug(config.username)
    config.save()
    config.read_config("/Users/huangzehui/.others")
    config.username = random.choice(["user2", ])
    logger.debug(config.host)
    logger.debug(config.username)
    config.save()
