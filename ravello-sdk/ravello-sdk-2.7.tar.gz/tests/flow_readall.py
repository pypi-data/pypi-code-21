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
import random
from support import *
from ravello_sdk import *


class TestReadAll(IntegrationTest):

    def test_get_applications(self):
        apps = self.client.get_applications()
        apps = random.sample(apps, min(10, len(apps)))
        self.assertIsInstance(apps, list)
        for app in apps:
            self.assertIsInstance(app, dict)
            self.assertIn('id', app)
            self.assertIn('name', app)
            self.assertIn('_href', app)
            app2 = self.client.reload(app)
            self.assertTrue(set(app).issubset(set(app2)))

    def test_get_blueprints(self):
        bps = self.client.get_blueprints()
        bps = random.sample(bps, min(10, len(bps)))
        self.assertIsInstance(bps, list)
        for bp in bps:
            self.assertIsInstance(bp, dict)
            self.assertIn('id', bp)
            self.assertIn('name', bp)
            self.assertIn('_href', bp)
            bp2 = self.client.reload(bp)
            self.assertTrue(set(bp).issubset(set(bp2)))

    def test_get_images(self):
        images = self.client.get_images()
        images = random.sample(images, min(10, len(images)))
        self.assertIsInstance(images, list)
        for img in images:
            self.assertIsInstance(img, dict)
            self.assertIn('id', img)
            self.assertIn('name', img)
            self.assertIn('_href', img)
            img2 = self.client.reload(img)
            # Idiosyncracy: the images list sometimes shows {} for CM, while
            # the individual image has an absent key.
            img.setdefault('configurationManagement', {})
            img2.setdefault('configurationManagement', {})
            self.assertTrue(set(img).issubset(set(img2)))

    def test_get_keypairs(self):
        kps = self.client.get_keypairs()
        kps = random.sample(kps, min(10, len(kps)))
        self.assertIsInstance(kps, list)
        for kp in kps:
            self.assertIsInstance(kp, dict)
            self.assertIn('id', kp)
            self.assertIn('name', kp)
            self.assertIn('_href', kp)
            kp2 = self.client.reload(kp)
            self.assertTrue(set(kp).issubset(set(kp2)))


if __name__ == '__main__':
    unittest.main()
