# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2012 Jens Lindström, Opera Software ASA
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

import json
import os
import sys
import pkg_resources

class Error(Exception):
    pass

class ImplementationError(Error):
    pass

class InvalidConfiguration(Error):
    pass

class MissingConfiguration(Error):
    pass

def settings_dir():
    # If installed in a virtual environment (default case) then return a sub-
    # directory inside the virtual environment.
    if sys.prefix != sys.base_prefix:
        return os.path.join(sys.prefix, "etc")
    # Otherwise, fall back to a reasonable system directory.
    return "/etc/critic"

def configuration():
    try:
        with open(os.path.join(settings_dir(), "configuration.json")) as file:
            return json.load(file)
    except ValueError:
        raise InvalidConfiguration()
    except OSError:
        raise MissingConfiguration()
