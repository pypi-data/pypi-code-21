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
Control the formatting and display of returned output.
"""
from __future__ import print_function
import json
import logging
from collections import OrderedDict
from tabulate import tabulate, tabulate_formats

from ncloud.config import config

logger = logging.getLogger()


class TableFormatter(object):
    """handles formatting all table output"""
    def __init__(self, json):
        # TODO: implement? use this import
        # from backports.shutil_get_terminal_size import get_terminal_size
        # self.term_columns, self.term_lines = get_terminal_size()
        self.calc_table_data(json)

    def calc_table_data(self, json):
        """expose table data calculation function in case want to re-eval"""
        self.headers, self.rows = self._get_key_values(json)
        self.rows = self._clean_rows()

    def _get_key_values(self, json):
        if len(json) == 0:
            return [], []

        if isinstance(json, list):
            keys = list(json[0].keys())
            values = [list(row.values()) for row in json]
        else:
            keys = list(json.keys())
            values = [list(json.values())]
        return keys, values

    def _clean_rows(self):
        return list(map(lambda x: self._clean_item(x), row)
                    for row in self.rows)

    def _clean_item(self, item):
        if isinstance(item, list):
            return ''.join(self._clean_item(elem) for elem in item)
        elif isinstance(item, OrderedDict):
            item = json.dumps(item)
            return item
        else:
            item = str(item)
            return item


def print_table(json):
    if json is None:
        return
    formatter = TableFormatter(json)
    output_format = config.get_output_format()
    if output_format not in tabulate_formats:
        print('Table format not valid. Tabulate defaults to simple format.')
    print(tabulate(
        formatter.rows, headers=formatter.headers, tablefmt=output_format))


class RequestError(Exception):
    pass


def print_error(err):
    if err is not None:
        msg = err.text.strip()
        try:
            json_msg = json.loads(msg)
            if "status" in json_msg:
                msg = json_msg["status"]
        except ValueError:
            pass

        multiline = '\n' in msg
        if multiline:
            print(msg)
        else:
            print_table({"error_code": err.status_code, "message": msg})

    else:
        logger.error("No error message in response")
    raise RequestError()
