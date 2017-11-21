# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from os.path import expanduser
import subprocess
import sys

from altuscli.extensions.dataeng import DEVNULL
from altuscli.extensions.dataeng import SOCKS_PORT
from altuscli.extensions.dataeng import which


def open_web_browser_with_socks(url):
    if sys.platform.startswith("win"):
        return open_chrome(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                           url)
    elif sys.platform.startswith("linux"):
        return open_chrome("/usr/bin/google-chrome",
                           url)
    elif sys.platform.startswith("darwin"):
        return open_chrome("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                           url)
    else:
        print('Could not open Cloudera Manager on Google Chrome browser in {0} OS'
              .format(sys.platform))
        return False


def open_chrome(process, url):
    user_dir = '--user-data-dir={0}chrome-with-proxy'.format(expanduser("~") + os.sep)
    proxy = '--proxy-server=socks5://localhost:' + SOCKS_PORT

    if which(process) is not None:
        command = [process, user_dir, proxy, url]
        print('Browser command: ' + ' '.join(command))
        subprocess.Popen(command,
                         stdout=DEVNULL, stderr=subprocess.STDOUT)
        return True
    else:
        print('The Google Chrome browser could not be found at: ' + process)
        return False
