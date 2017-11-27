import unittest2 as unittest

from mortar.api.v2 import cluster_configurations

from requests.exceptions import HTTPError

import mock

class TestClusterConfigurations(unittest.TestCase):

    def setUp(self):
        self.api_mock = mock.Mock()
    
    def test_get_cluster_configuration(self):
        response = {
            "cluster_size": 32
        }
        self.api_mock.get.return_value = response
        return_cc = cluster_configurations.get_cluster_configuration(self.api_mock, "some_name")
        self.assertEquals(return_cc, response)

    def test_get_cc_not_found(self):
        response_mock_404 = mock.Mock()
        response_mock_404.status_code = 404
        response_mock_404.reason = 'Not Found'
        response_mock_404.text = 'The resource could not be found.'
        self.api_mock.get.side_effect = HTTPError('Message', response=response_mock_404)
        return_cc = cluster_configurations.get_cluster_configuration(self.api_mock, "notfound")
        self.assertIsNone(return_cc)
