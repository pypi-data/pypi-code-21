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

from altuscli import exceptions

from altuscli.extensions.dataeng import which


def validate_ssh_with_key_file(key_file):
    if (which('putty.exe') or which('ssh') or which('ssh.exe')) is None:
        raise exceptions.SSHNotFoundError
    else:
        check_ssh_key_format(key_file)


def check_ssh_key_format(key_file):
    # If only putty is present and the file format is incorrect
    if which('putty.exe') is not None and (which('ssh.exe') or which('ssh')) is None:
        if check_command_key_format(key_file, ['ppk']) is False:
            raise exceptions.WrongPuttyKeyError
    else:
        pass


def check_command_key_format(key_file, accepted_file_format=None):
    if accepted_file_format is None:
        accepted_file_format = []
    if any(key_file.endswith(i) for i in accepted_file_format):
        return True
    else:
        return False
