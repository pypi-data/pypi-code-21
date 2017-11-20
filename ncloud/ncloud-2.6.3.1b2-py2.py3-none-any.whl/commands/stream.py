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
Subcommands for performing stream predictions using deployed models.
"""
from __future__ import print_function
import io
import zipfile
import os
import sys
import json
from functools import partial
import logging
import requests
import time

from ncloud.config import STREAM_PREDICTIONS
from ncloud.formatting.time_zone import utc_to_local
from ncloud.commands.command import (BaseList, Command, print_table,
                                     build_subparser)
from ncloud.commands.command import SHOW, UNDEPLOY, PREDICT
from ncloud.completers import ModelCompleter

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
        undeploy.add_argument(
            "stream_id", type=int,
            help="ID of stream to undeploy."
        ).completer = ModelCompleter

        undeploy.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, stream_id):
        delete_path = os.path.join(STREAM_PREDICTIONS, str(stream_id))
        return Undeploy.api_call(
            config, delete_path, method="DELETE", return_json=True)


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
        list_stream_prediction.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        vals = List.BASE_ARGS
        return List.api_call(
            config, STREAM_PREDICTIONS, params=vals, return_json=True)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res['predictions'])


class Show(Command):
    """
    Show stream prediction details for a given stream ID.
    """
    @classmethod
    def parser(cls, subparser):
        stream_predict_show = subparser.add_parser(
            SHOW.name, aliases=SHOW.aliases,
            help=Show.__doc__, description=Show.__doc__
        )
        stream_predict_show.add_argument(
            "stream_id", type=int,
            help="ID of stream to show details of."
        )
        stream_predict_show.add_argument(
            "-l", "--log", action="store_true",
            help="Show console log from predict runtime.")
        stream_predict_show.add_argument(
            "-L", "--log-follow", action="store_true",
            help="Show console log from predict runtime as the data grows." +
                 "Similar to how tail -f works on a UNIX-based machine.")

        stream_predict_show.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, stream_id, log=False, log_follow=False):
        show_path = os.path.join(STREAM_PREDICTIONS, str(stream_id))
        if log:
            write = getattr(sys.stdout, 'buffer', sys.stdout).write
            res = Show.api_call(config, show_path, params={'log': 'True'})
            try:
                write(zipfile.ZipFile(io.BytesIO(res)).read('krypton.log'))
            except KeyError:
                logger.warning("attempting to view non-existent krypton.log")
            return
        elif log_follow:
            # make a session so we can make repeated calls in the same session
            sess = requests.session()
            # we will fetch the krypton file data only!
            result, status_code = Show.api_call(
                config, show_path, stream=True, session=sess,
                params={'log_follow': 'True'}, return_status_code=True)
            log_data = json.loads(result)
            if not log_data.get('results'):
                logger.warning("attempting to view non-existent krypton.log")
                return
            log_maybe_finished = False
            while True:
                try:
                    # get the data from each request
                    # write the results out and use the offset to fetch more
                    # data from that point
                    results = log_data['results']
                    offset = log_data['offset']
                    if results:
                        print(results)
                    # wait 2.5 sec before fetching more data again
                    # if 200 status code, else break if 202
                    if log_maybe_finished and status_code == 202:
                        return
                    log_maybe_finished = status_code == 202
                    time.sleep(2.5)
                    # continue making requests, displaying more data until user
                    # says to stop
                    result, status_code = Show.api_call(
                        config, show_path, stream=True, session=sess,
                        params={'offset': offset, 'log_follow': 'True'},
                        return_status_code=True)
                    log_data = json.loads(result)
                except KeyboardInterrupt:
                    # graceful exit on keyboard interrupt
                    sys.exit(0)

        res = Show.api_call(config, show_path, return_json=True)

        for tm in ["time_launched"]:
            if tm in res and res[tm] is not None:
                res[tm] = utc_to_local(res[tm])

        return res


parser = partial(
    build_subparser, 'stream', ['s'], __doc__, (List, Show, Undeploy, Predict)
)
