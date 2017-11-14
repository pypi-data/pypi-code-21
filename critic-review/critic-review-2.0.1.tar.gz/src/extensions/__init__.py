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

import os

def getExtensionPath(critic, author_name, extension_name):
    return extension.Extension(critic, author_name, extension_name).getPath()

def getExtensionInstallPath(critic, sha1):
    return os.path.join(critic.settings.extensions.install_dir, sha1)

def checkEnabled(critic):
    if not critic.settings.extensions.enabled:
        import dbutils
        import page.utils
        administrators = dbutils.getAdministratorContacts(
            critic.database, as_html=True)
        raise page.utils.DisplayMessage(
            title="Extension support not enabled",
            body=(("<p>This Critic system does not support extensions.</p>"
                   "<p>Contact %s to have it enabled, or see the "
                   "<a href='/tutorial?item=administration#extensions'>"
                   "section on extensions</a> in the system administration "
                   "tutorial for more information.</p>")
                  % administrators),
            html=True)

from . import manifest
from . import extension
from . import resource
