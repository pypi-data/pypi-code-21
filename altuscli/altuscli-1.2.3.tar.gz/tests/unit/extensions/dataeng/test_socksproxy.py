# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2017 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from altuscli.extensions.dataeng.socksproxy import SocksProxyCommand

import mock

from tests import unittest

from . import SAMPLE_DESCRIBE_CLUSTER
from .. import FakeArgs


class TestSocksProxyCommand(unittest.TestCase):
    def setUp(self):
        self.session = mock.Mock()

    @mock.patch('altuscli.extensions.dataeng.dataengutils.get_cluster')
    def test_socks_proxy_command(self, get_cluster_mock):
        socks_command = SocksProxyCommand(self.session)
        parsed_globals = mock.Mock()
        client_creator = mock.Mock()
        get_cluster_mock.return_value = SAMPLE_DESCRIBE_CLUSTER['cluster']

        # Setup socks proxy only
        parsed_args = FakeArgs(cluster_name='cloudtrail-analyze-final',
                               ssh_private_key='file:///root/.ssh/ec2_rsa')

        with mock.patch('altuscli.extensions.dataeng.sshutils.which') as mock_which:
            with mock.patch('subprocess.Popen') as mock_popen:
                process = mock.Mock()
                process.poll.return_value = 0
                process.returncode = 0
                mock_popen.return_value = process
                mock_which.return_value = '/some/path'

                socks_command._run_main(client_creator, parsed_args, parsed_globals)
                self.assertEqual(mock_popen.call_count, 1)

        # Setup socks proxy and open browser
        parsed_args.__setattr__('open_cloudera_manager', 'yes')
        parsed_args.__setattr__('ssh_private_key', '/root/.ssh/ec2_rsa')

        with mock.patch('altuscli.extensions.dataeng.browserutils.which') as mock_which_1:  # noqa
            with mock.patch('altuscli.extensions.dataeng.sshutils.which') as mock_which_2:  # noqa
                with mock.patch('subprocess.Popen') as mock_popen:
                    process = mock.Mock()
                    process.poll.side_effect = [None, None, None, None, 0]
                    process.returncode = 0
                    mock_popen.return_value = process
                    mock_which_1.return_value = '/some/path'
                    mock_which_2.return_value = '/some/path'

                    socks_command._run_main(client_creator, parsed_args, parsed_globals)
                    self.assertEqual(mock_popen.call_count, 2)
