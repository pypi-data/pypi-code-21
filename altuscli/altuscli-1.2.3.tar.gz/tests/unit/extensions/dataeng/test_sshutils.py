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

from altuscli.extensions.dataeng import sshutils
from altuscli.extensions.dataeng import which

import mock

from tests import skip_if_windows
from tests import unittest


class TestSSHUtils(unittest.TestCase):

    @mock.patch('altuscli.extensions.dataeng.sshutils.which')
    def test_ssh_key_file_format(self, mock_which):
        def which_side_effect(program):
            if program == 'ssh' or program == 'scp':
                return '/some/path'
        mock_which.side_effect = which_side_effect

        sshutils.validate_ssh_with_key_file('key.abc')

        sshutils.validate_ssh_with_key_file('key')

        self.assertTrue(sshutils.check_command_key_format('key.ppk', ['ppk']))

        self.assertFalse(sshutils.check_command_key_format('key.pem', ['ppk']))

    @skip_if_windows("Test not valid on windows.")
    def test_which_with_existing_command(self):
        # We do not support non unix dev environment
        pythonPath = which('/usr/bin/python3') or which('/usr/bin/python')
        self.assertNotEqual(pythonPath, None)

    def test_which_with_non_existing_command(self):
        path = which('klajsflklj')
        self.assertEqual(path, None)
