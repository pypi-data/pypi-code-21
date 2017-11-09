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

import unittest

from ubersmith_client import _http_utils


class HttpUtilsTest(unittest.TestCase):
    def test_form_encode_with_list(self):
        result = _http_utils.form_encode(dict(test=['a', 'b']))
        self.assertDictEqual({
            'test[0]': 'a',
            'test[1]': 'b',
        }, result)

    def test_with_tuples(self):
        result = _http_utils.form_encode(dict(test=('a', 'b')))

        self.assertDictEqual({
            'test[0]': 'a',
            'test[1]': 'b',
        }, result)

    def test_with_dict(self):
        result = _http_utils.form_encode(dict(test={'a': '1', 'b': '2'}))

        self.assertDictEqual({
            'test[a]': '1',
            'test[b]': '2'
        }, result)

    def test_with_empty_dict(self):
        result = _http_utils.form_encode(dict(test_dict={}, test_list=[]))

        self.assertDictEqual({
            'test_dict': {},
            'test_list': []
        }, result)

    def test_with_nested_lists_and_dicts(self):
        result = _http_utils.form_encode(dict(test=[['a', 'b'], {'c': '1', 'd': '2'}]))

        self.assertDictEqual({
            'test[0][0]': 'a',
            'test[0][1]': 'b',
            'test[1][c]': '1',
            'test[1][d]': '2'
        }, result)

    def test_with_bools(self):
        result = _http_utils.form_encode(dict(true=True, false=False))

        self.assertDictEqual({
            'true': True,
            'false': False
        }, result)

    def test_filtering_files(self):
        result = _http_utils.form_encode_without_files(dict(true=True, files=dict(attach='some_binary_data')))
        self.assertDictEqual({
            'true': True,
        }, result)
