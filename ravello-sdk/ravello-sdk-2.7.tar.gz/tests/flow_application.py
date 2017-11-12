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
import copy

from support import *
from ravello_sdk import *


class TestApplication(IntegrationTest):

    @property
    def created(self):
        return getattr(type(self), 'created', None)

    @property
    def keypair(self):
        return getattr(type(self), 'keypair', None)

    def test_aa_create_application(self):
        keypair = {'name': self.random_name(), 'publicKey': self.pubkey}
        keypair = self.client.create_keypair(keypair)
        self.assertIsInstance(keypair, dict)
        self.assertIsInstance(keypair['id'], six.integer_types)
        type(self).keypair = keypair
        imgid = self.config.getint('integration', 'image')
        image = self.client.get_image(imgid)
        self.assertIsInstance(image, dict)
        self.assertIsInstance(image['id'], six.integer_types)
        vm = copy.deepcopy(image)
        update_luids(vm)
        vm.update({'name': 'vm1', 'hostnames': ['vm1'],
                   'keypairId': self.keypair['id']})
        application = {'name': self.random_name(), 'publicKey': self.pubkey,
                       'design': {'vms': [vm]}}
        created = self.client.create_application(application)
        self.assertIsInstance(created, dict)
        self.assertIsInstance(created['id'], six.integer_types)
        self.assertIsInstance(created['name'], six.string_types)
        type(self).created = created

    def test_ab_publish_application(self):
        created = self.created
        if created is None:
            raise SkipTest('creation failed')
        self.client.publish_application(created)
        self.client.wait_for(created, lambda app: application_state(app) == 'STARTED', 600)
        type(self).created = self.client.get_application(created)

    def test_ac_stop_application(self):
        created = self.created
        if created is None or application_state(created) != 'STARTED':
            raise SkipTest('creation or start failed')
        self.client.stop_application(created)
        self.client.wait_for(created, lambda app: application_state(app) == 'STOPPED', 600)
        type(self).created = self.client.get_application(created)

    def test_ad_start_application(self):
        created = self.created
        if created is None or application_state(created) != 'STOPPED':
            raise SkipTest('creation or stop failed')
        self.client.start_application(created)
        self.client.wait_for(created, lambda app: application_state(app) == 'STARTED', 600)
        type(self).created = self.client.get_application(created)

    def test_ae_get_vnc_url(self):
        created = self.created
        if created is None or application_state(created) != 'STARTED':
            raise SkipTest('creation or start failed')
        vm = created['deployment']['vms'][0]
        url = self.client.get_vnc_url(created, vm)
        self.assertIsInstance(url, six.text_type)
        self.assertTrue(url.startswith('https://'))
        self.assertTrue('ravellosystems.com' in url)

    def test_zz_delete_application(self):
        created = self.created
        if created is None:
            raise SkipTest('creation failed')
        self.client.delete_application(created)
        app = self.client.get_application(created['id'])
        self.assertIsNone(app)
        self.client.delete_keypair(self.keypair)


if __name__ == '__main__':
    unittest.main()
