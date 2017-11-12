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

import six
from support import *
from ravello_sdk import *


class TestDiskImage(IntegrationTest):

    def test_get_diskimage(self):
        imgid = self.config.getint('integration', 'diskimage')
        image = self.client.get_diskimage(imgid)
        self.assertIsInstance(image, dict)
        self.assertIsInstance(image['id'], six.integer_types)
        self.assertEqual(image['id'], imgid)
        self.assertIsInstance(image['name'], six.string_types)

    def test_get_diskimages(self):
        imgid = self.config.getint('integration', 'diskimage')
        images = self.client.get_diskimages()
        self.assertIsInstance(images, list)
        for image in images:
            self.assertIsInstance(image, dict)
        images = list(filter(lambda img: img['id'] == imgid, images))
        self.assertIsInstance(images, list)
        self.assertEqual(len(images), 1)
        self.assertIsInstance(images[0], dict)
        image = images[0]
        images = self.client.get_diskimages({'id': image['id']})
        self.assertEqual(images, [image])
        images = self.client.get_diskimages({'name': image['name']})
        self.assertEqual(images, [image])


if __name__ == '__main__':
    unittest.main()
