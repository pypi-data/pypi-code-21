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
Subcommands for performing stream predictions using deployed models.
"""
from __future__ import print_function

import json
import logging
import sys
from functools import partial

import os

from ncloud.commands.command import (BaseList, Command, print_table,
                                     build_subparser, ShowLogs, Results)
from ncloud.commands.command import SHOW, UNDEPLOY, PREDICT
from ncloud.completers import ModelCompleter, StreamCompleter
from ncloud.config import STREAM_PREDICTIONS
from ncloud.formatting.time_zone import utc_to_local

logger = logging.getLogger()


class Undeploy(Command):
    """
    Remove a deployed model.
    """

    @classmethod
    def parser(cls, subparser):
        undeploy = subparser.add_parser(
            UNDEPLOY.name, aliases=UNDEPLOY.aliases,
            help=Undeploy.__doc__, description=Undeploy.__doc__
        )
        group = undeploy.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "stream_ids", type=int, nargs="*", default=[],
            help="ID of stream to undeploy.",
        ).completer = ModelCompleter

        group.add_argument("-a", "--all_streams", action="store_true",
                           help="Undeploy all streams user has access to")

        undeploy.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, stream_ids, all_streams=False):

        return Undeploy.api_call(
            config, STREAM_PREDICTIONS+"/", method="Delete", return_json=True,
            params={'stream_ids': stream_ids}
        )


class Predict(Command):
    """
    Generate predicted outcomes from a deployed model and input data.
    """

    @classmethod
    def parser(cls, subparser):
        predict = subparser.add_parser(
            PREDICT.name, aliases=PREDICT.aliases,
            help=Predict.__doc__, description=Predict.__doc__
        )
        predict.add_argument(
            "presigned_token",
            help="Presigned token for sending prediction requests."
        )
        predict.add_argument(
            "input",
            help="Input data filename or url to generate predictions for."
        )
        predict.add_argument(
            "-t", "--in-type",
            default="image",
            help="Type of input.  Valid choices are: image (default), json"
        )
        predict.add_argument(
            "-f", "--formatter", default="raw",
            choices=('raw', 'classification'),
            help="How to format predicted outputs from the network. Valid "
                 "choices are: raw (default), classification"
        )
        predict.add_argument(
            "-a", "--args",
            help="Additional arguments for the formatter. These vary, details "
                 "can be found at: http://doc.cloud.nervanasys.com (Output "
                 "Formatters)"
        )

        predict.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, presigned_token, input, in_type=None, formatter=None,
             args=None):

        vals = {}
        files = None

        if input.startswith("http") or input.startswith("s3"):
            vals["url"] = input
        elif os.path.exists(input):
            files = [('input', (os.path.basename(input), open(input, "rb")))]
        else:
            print("no/invalid input data specified")
            sys.exit(1)

        if in_type:
            vals["type"] = in_type
        if formatter:
            vals["formatter"] = formatter
        if args:
            vals["args"] = args

        if not presigned_token.isdigit():
            endpoint = os.path.join(STREAM_PREDICTIONS, presigned_token)
        else:
            endpoint = os.path.join('/predictions/', presigned_token)
        return Predict.api_call(
            config, endpoint, method="POST", data=vals, files=files,
            add_ncloud_data=False, return_json=True,
            headers={'HOST': 'stream.nervanasys.com'})

    @staticmethod
    def display_after(config, args, res):
        if not args.formatter or args.formatter == "raw":
            print(json.dumps(res))
        else:
            if "predictions" in res:
                print_table(res["predictions"])
            else:
                print_table(res)


class List(BaseList):
    """
    List all stream prediction deployments.
    """

    @classmethod
    def parser(cls, subparser):
        list_stream_prediction = super(List, cls).parser(
            subparser, List.__doc__, List.__doc__)
        list_stream_prediction.add_argument(
            "-d", "--details", action="store_true",
            help="Show a more detailed stream prediction list."
        )
        list_stream_prediction.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, details=False):
        vals = List.BASE_ARGS
        vals['details'] = details
        return List.api_call(
            config, STREAM_PREDICTIONS, params=vals, return_json=True)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res['predictions'])


class Show(ShowLogs):
    """
    Show stream prediction details for a given stream ID.
    """

    @classmethod
    def parser(cls, subparser):
        stream_predict_show = super(Show, cls).parser(
            subparser, SHOW.aliases, Show.__doc__, Show.__doc__
        )

        stream_predict_show.add_argument(
            "stream_id", type=int,
            help="ID of stream to show details of."
        )
        stream_predict_show.add_argument(
            "-d", "--details", action="store_true",
            help="Show a more detailed stream prediction."
        )
        stream_predict_show.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, stream_id, log=False, log_follow=False, details=False):
        show_path = os.path.join(STREAM_PREDICTIONS, str(stream_id), 'outputs',
                                 'krypton.log')
        details_path = os.path.join(STREAM_PREDICTIONS, str(stream_id))
        if not (log or log_follow):
            res = Show.api_call(config, details_path, return_json=True,
                                params={'details': details})

            for tm in ["time_launched"]:
                if tm in res and res[tm] is not None:
                    res[tm] = utc_to_local(res[tm])

            return res

        if log:
            params = {'format': 'zip', 'log_file': 'krypton.log'}

            ShowLogs.read_log(config, show_path, params)

        elif log_follow:
            params = {'tail': 'True', 'log_file': 'krypton.log'}
            ShowLogs.read_log_tail(config, show_path, params)


StreamResults = Results(
    "stream",
    StreamCompleter,
    STREAM_PREDICTIONS
)

parser = partial(
    build_subparser, 'stream', ['s'], __doc__, (
        List, Show, Undeploy, Predict, StreamResults
    )
)
