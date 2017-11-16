# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Subcommands for getting the supported environments.
"""
import logging
from functools import partial
from ncloud.commands.command import (BaseList, build_subparser)
from ncloud.config import ENVIRONMENTS

logger = logging.getLogger()


class List(BaseList):
    """
    List the supported environments.
    """
    @classmethod
    def parser(cls, subparser):
        environments = super(List, cls).parser(
            subparser, List.__doc__, List.__doc__)
        environments.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        vals = List.BASE_ARGS

        return List.api_call(config, ENVIRONMENTS, params=vals,
                             return_json=True)

parser = partial(
    build_subparser, 'environment', ['e'], __doc__,
    (List, )

)
