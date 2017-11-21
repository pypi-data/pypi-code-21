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

from altuscli.extensions.dataeng import browserutils

import mock

from tests import unittest


class TestBrowserUtils(unittest.TestCase):

    def test_unsupported_system(self):
        with mock.patch('sys.platform', 'Solaris'):
            self.assertFalse(
                browserutils.open_web_browser_with_socks('http://www.cloudera.com'))

    @mock.patch('subprocess.Popen')
    def test_open_chrome(self, mock_popen):
        with mock.patch('altuscli.extensions.dataeng.browserutils.which') as mock_which:
            mock_which.return_value = '/some/path'
            browserutils.open_web_browser_with_socks('http://www.cloudera.com')
            self.assertEqual(mock_popen.call_count, 1)

    def test_chrome_not_installed(self):
        with mock.patch('altuscli.extensions.dataeng.browserutils.which') as mock_which:
            mock_which.return_value = None
            self.assertFalse(browserutils.open_chrome("/usr/bin/google-chrome",
                                                      "http://www.cloudera.com"))
