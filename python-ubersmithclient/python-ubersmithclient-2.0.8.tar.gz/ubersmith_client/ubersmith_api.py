# Copyright 2017 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ubersmith_client.ubersmith_request_get import UbersmithRequestGet
from ubersmith_client.ubersmith_request_post import UbersmithRequestPost


class UbersmithApi(object):
    def __init__(self, url, user, password, timeout, use_http_get):
        self.url = url
        self.user = user
        self.password = password
        self.timeout = float(timeout)
        self.ubersmith_request = UbersmithRequestGet if use_http_get else UbersmithRequestPost

    def __getattr__(self, module):
        return self.ubersmith_request(self.url, self.user, self.password, module, self.timeout)
