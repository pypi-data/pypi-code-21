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
Time zone conversion functionality
"""
import calendar
from datetime import datetime


def utc_to_local(utc_string):
    utc = datetime.strptime(utc_string, "%a, %d %b %Y %H:%M:%S GMT")
    local_timestamp = calendar.timegm(utc.timetuple())
    local_time = datetime.fromtimestamp(local_timestamp)
    formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S %Z").rstrip()
    return formatted_time


def utcstr_to_date(utc_string):
    utc = datetime.strptime(utc_string, "%a, %d %b %Y %H:%M:%S GMT")
    formatted_time = utc.strftime("%Y-%m-%d %H:%M:%S %Z").rstrip()
    return formatted_time
