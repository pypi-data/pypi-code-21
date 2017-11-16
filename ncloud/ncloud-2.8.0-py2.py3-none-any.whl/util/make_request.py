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

import ast
from ncloud import __version__
from ncloud.config import config
from ncloud.util.request_processor import NcloudRequest
from ncloud.vendor.python.argparse import ArgumentParser
from ncloud.vendor.python.argparse import ArgumentDefaultsHelpFormatter


def main(conf):
    parser = ArgumentParser(description=__doc__, prog="make_request",
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--host", default=conf.get_host(),
                        help="Nervana cloud host to connect to.")
    parser.add_argument("--api-ver", default=conf.get_default_api_ver(),
                        help="Nervana cloud API version to use.")
    parser.add_argument("--auth-host",
                        default=conf.get_default_auth_host(),
                        help="Nervana host to connect to to perform "
                             "authorization.")
    parser.add_argument("--tenant", default=conf.get_default_tenant(),
                        help="Tenant name to use for requests.")
    parser.add_argument("--table-format", default="psql",
                        help="Display format. Defaults to psql. "
                        "See https://pypi.python.org/pypi/tabulate"
                        "for more options.")
    parser.add_argument("-d", "--data", type=str,
                        help="A json-formatted "
                        "object to send to the endpoint")
    parser.add_argument("method", type=str,
                        help="The HTTP method you want to use")
    parser.add_argument("endpoint", type=str,
                        help="The last part of "
                        "the endpoint url. Ex. /tenants/all/")
    return parser.parse_args()


if __name__ == '__main__':
    args = main(config)
    config.set_defaults(args)
    if args.data:
        args.data = ast.literal_eval(args.data)
    res = NcloudRequest().make_call(config, args.endpoint, method=args.method,
                                    params=args.data, data=args.data)
    print(res)
