# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2017 the Critic contributors, Opera Software ASA
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import base64
import hashlib
import pkg_resources

class NotFound(Exception):
    pass

RESOURCE_HASH_CACHE = {}

def fetch(filename):
    if not pkg_resources.resource_exists(__name__, filename):
        raise NotFound
    resource_string = pkg_resources.resource_string(__name__, filename)
    resource_hash = RESOURCE_HASH_CACHE.get(filename)
    if resource_hash is None:
        digest = hashlib.sha1(resource_string).digest()
        resource_hash = base64.b32encode(digest).decode()
        RESOURCE_HASH_CACHE[filename] = resource_hash
    return resource_string, resource_hash
