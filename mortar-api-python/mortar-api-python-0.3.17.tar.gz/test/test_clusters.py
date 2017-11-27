#
# Copyright 2013 Mortar Data Inc.
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
#

import unittest

from mortar.api.v2 import clusters

import mock

class TestClusters(unittest.TestCase):

    def setUp(self):
        self.api_mock = mock.Mock()
        self.project_name = 'my_project'
        self.script_name = 'my_script'
    
    def test_get_clusters(self):
        response = [{'cluster_id': 'abc'},
                    {'cluster_id': 'xyz'}]
        self.api_mock.get.return_value = response
        return_clusters = clusters.get_clusters(self.api_mock)
        self.assertEquals(return_clusters, response)

    def test_stop_cluster(self):
        self.api_mock.delete.return_value = None
        clusters.stop_cluster(self.api_mock, '123456')
        self.api_mock.delete.assert_called_with('clusters/123456')
