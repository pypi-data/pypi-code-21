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

import copy

from altuscli import exceptions
from altuscli.extensions.dataeng import dataengutils

import mock

from tests import unittest

from . import SAMPLE_DESCRIBE_CLUSTER


class TestDataEngUtils(unittest.TestCase):

    def setUp(self):
        self.cluster_response = SAMPLE_DESCRIBE_CLUSTER

    @mock.patch('altuscli.extensions.dataeng.dataengutils.get_client')
    def test_get_cluster(self, get_client_mock):
        client = mock.Mock()
        get_client_mock.return_value = client
        client.describe_cluster.return_value = self.cluster_response

        cluster = dataengutils.get_cluster(None, None, 'cluster-name')

        self.assertTrue(client.describe_cluster.called)
        client.describe_cluster.assert_called_with(clusterName='cluster-name')
        self.assertEqual(cluster, self.cluster_response['cluster'])

    def test_get_cm_endpoint(self):
        self.assertEqual(dataengutils.get_cm_endpoint(
            self.cluster_response["cluster"],
            'cluster-name'),
            self.cluster_response["cluster"]["clouderaManagerEndpoint"])

    def test_get_terminating_cluster_cm_endpoint(self):
        local_clusters = copy.deepcopy(self.cluster_response)
        local_clusters['cluster']['status'] = 'TERMINATING'

        with self.assertRaises(exceptions.ClusterTerminatingError):
            dataengutils.get_cm_endpoint(local_clusters['cluster'],
                                         'cluster-name')
