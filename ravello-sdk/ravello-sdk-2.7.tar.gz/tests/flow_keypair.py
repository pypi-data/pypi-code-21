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


class TestKeypair(IntegrationTest):

    @property
    def created(self):
        return getattr(type(self), 'created', None)

    def test_aa_create_keypair(self):
        keypair = {'name': self.random_name(), 'publicKey': self.pubkey}
        created = self.client.create_keypair(keypair)
        self.assertIsInstance(created, dict)
        self.assertIsInstance(created['id'], six.integer_types)
        self.assertEqual(created['name'], keypair['name'])
        self.assertFalse('publicKey' in created)
        self.assertFalse('privateKey' in created)
        type(self).created = created

    def test_get_keypair(self):
        if self.created is None:
            raise SkipTest('creation failed')
        keypair = self.client.get_keypair(self.created['id'])
        self.assertEqual(keypair, self.created)

    def test_get_keypairs(self):
        created = self.created
        if created is None:
            raise SkipTest('creation failed')
        keypairs = self.client.get_keypairs()
        keypairs = list(filter(lambda kp: kp['id'] == created['id'], keypairs))
        self.assertEqual(len(keypairs), 1)
        created = copy.deepcopy(created)
        self.assertEqual(keypairs[0], created)
        keypairs = self.client.get_keypairs({'name': created['name']})
        self.assertEqual(len(keypairs), 1)
        self.assertEqual(keypairs[0], created)

    def test_yy_update_keypair(self):
        created = self.created
        if created is None:
            raise SkipTest('creation failed')
        keypair = self.client.get_keypair(created['id'])
        self.assertIsNotNone(keypair)
        keypair['name'] = self.random_name()
        updated = self.client.update_keypair(keypair)
        self.assertEqual(updated, keypair)
        updated = self.client.get_keypair(created['id'])
        self.assertEqual(updated, keypair)

    def test_zz_delete_keypair(self):
        created = self.created
        if created is None:
            raise SkipTest('creation failed')
        keypair = self.client.get_keypair(created['id'])
        self.assertIsNotNone(keypair)
        self.assertFalse(keypair.get('deleted'))
        self.client.delete_keypair(created['id'])
        keypair = self.client.get_keypair(created['id'])
        self.assertIsNotNone(keypair)
        self.assertTrue(keypair.get('deleted'))

    def test_generate_keypair(self):
        keypair = self.client.generate_keypair()
        self.assertIsInstance(keypair, dict)
        self.assertIsInstance(keypair['publicKey'], six.string_types)
        self.assertGreater(len(keypair['publicKey']), 100)
        self.assertIsInstance(keypair['privateKey'], six.string_types)
        self.assertGreater(len(keypair['privateKey']), 100)


if __name__ == '__main__':
    unittest.main()
