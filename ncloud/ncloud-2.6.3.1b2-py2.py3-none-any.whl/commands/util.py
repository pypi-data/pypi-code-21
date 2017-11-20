# ----------------------------------------------------------------------------
# Copyright 2015-2017 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
#
# # -*- coding: utf-8 -*-
"""
Subcommands for upgrading ncloud.
"""
import logging
import sys

from ncloud.config import INFO
from ncloud.commands.command import Command

logger = logging.getLogger()


class Info(Command):
    """
    Show version information.
    """
    @classmethod
    def parser(cls, subparser):
        info = subparser.add_parser("info",
                                    help=Info.__doc__,
                                    description=Info.__doc__)
        info.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        return Info.api_call(config, INFO, return_json=True)


class Upgrade(Command):
    """
    Upgrade ncloud to the latest version.
    """
    @classmethod
    def parser(cls, subparser):
        upgrade = subparser.add_parser("upgrade",
                                       help=Upgrade.__doc__,
                                       description=Upgrade.__doc__)
        upgrade.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        # pip is a slow import; placing here for speedup
        import pip
        try:
            pip.main(["install", "--upgrade", "ncloud"])
        except Exception as e:
            logger.error(e)
            sys.exit(1)
