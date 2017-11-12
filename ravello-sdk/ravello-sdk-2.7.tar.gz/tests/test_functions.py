# Copyright 2012-2014 Ravello Systems, Inc.
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

from __future__ import absolute_import, print_function

from support import *
from ravello_sdk import *


class TestNewName(UnitTest):

    def test_unique(self):
        names = ['foo-0', 'foo-1']
        new = new_name(names, 'foo-')
        self.assertNotIn(new, names)

    def test_format(self):
        names = ['foo-0', 'foo-1']
        new = new_name(names, 'foo-')
        self.assertEqual(new, 'foo-2')
        names = ['foo-0', 'foo-2']
        new = new_name(names, 'foo-')
        self.assertEqual(new, 'foo-1')

    def test_dict(self):
        names = [{'name': 'foo-0'}, {'name': 'foo-1'}]
        new = new_name(names, 'foo-')
        self.assertNotIn(new, names)


if __name__ == '__main__':
    unittest.main()
