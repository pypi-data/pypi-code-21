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

import logging
import os

import subprocess

import time

from altuscli.extensions.commands import BasicCommand
from altuscli.extensions.dataeng import browserutils
from altuscli.extensions.dataeng import dataengutils
from altuscli.extensions.dataeng import SOCKS_PORT
from altuscli.extensions.dataeng import SSH_USER
from altuscli.extensions.dataeng import sshutils
from altuscli.extensions.dataeng import which

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote

LOG = logging.getLogger('altuscli.extensions.dataeng.socksproxy')


class SocksProxyCommand(BasicCommand):
    NAME = 'socks-proxy'
    DESCRIPTION = ('Create a socks tunnel on port ' + SOCKS_PORT +
                   ' from your machine to the instance hosting'
                   ' cloudera manager.\n')
    ARG_TABLE = [
        {'name': 'cluster-name', 'required': True,
         'help_text': 'The name of the cluster you want to establish socks proxy.'},
        {'name': 'ssh-private-key', 'required': True,
         'no_paramfile': True,  # To disable the default paramfile behavior
         'help_text': 'The ssh private key. Please pass the same key, which is used '
                      'to create the cluster.'},
        {'name': 'open-cloudera-manager', 'required': False, 'choices': ['yes', 'no'],
         'help_text': 'Will open Cloudera Manager in Chrome browser if installed. '
                      'Valid choices are: ``yes`` | ``no``. '
                      'Defaults to ``no``.'},
    ]

    def _run_main(self, client_creator, parsed_args, parsed_globals):
        try:
            cluster_name = parsed_args.cluster_name
            cluster = dataengutils.get_cluster(
                client_creator=client_creator,
                parsed_globals=parsed_globals,
                cluster_name=cluster_name)

            endpoint = dataengutils.get_cm_endpoint(cluster, cluster_name)

            key_file = parsed_args.ssh_private_key
            # SSH does not accept file URIs, convert them to file path
            parts = urlparse(key_file)
            if 'file' == parts.scheme:
                key_file = os.path.abspath(os.path.join(parts.netloc, parts.path))
                key_file = os.path.normpath(unquote(key_file))
            sshutils.validate_ssh_with_key_file(key_file)
            if which('ssh') or which('ssh.exe'):
                command = ['ssh', '-o', 'ConnectTimeout=10', '-o',
                           'StrictHostKeyChecking=no', '-o', 'ServerAliveInterval=10',
                           '-CND', SOCKS_PORT, '-i', key_file, SSH_USER +
                           '@' + endpoint["publicIpAddress"]]
            else:
                command = ['putty', '-ssh', '-i', key_file,
                           SSH_USER + '@' + endpoint["publicIpAddress"], '-N', '-D',
                           SOCKS_PORT]

            print('Socks command: ' + ' '.join(command))
            process = subprocess.Popen(command)

            cm_url = "http://{0}:{1}/".format(endpoint["privateIpAddress"],
                                              endpoint["port"])
            wait_time = 0
            while process.poll() is None:
                time.sleep(1)
                wait_time += 1

                '''
                If the socks SSH command fails before 3 seconds it will exit this loop
                without opening the browser or printing the help text. If the command
                times out after 10 seconds, the console will display socks connection
                timed out and the browser will display socks connection refused error
                message if opened. Otherwise it will keep waiting and the user can send
                SIGINT to disable the socks tunnel.
                '''
                if wait_time == 3:
                    if 'open_cloudera_manager' in parsed_args \
                            and parsed_args.open_cloudera_manager == 'yes':
                        if not browserutils.open_web_browser_with_socks(cm_url):
                            self.print_browser_tip(cm_url)
                    else:
                        self.print_browser_tip(cm_url)

            if process.returncode != 0:
                if wait_time >= 9:
                    LOG.error('IP address of Cloudera Manager ({0}) is unreachable.'
                              ' Please check security permissions on instances of the'
                              ' cluster.'.format(endpoint["publicIpAddress"]))
                else:
                    LOG.error('Unable to setup socks tunnel.')
                return process.returncode

        except KeyboardInterrupt:
            print('Disabling Socks Tunnel.')
            return 0

    def print_browser_tip(self, cm_url):
        print('To open cloudera manager, please set the socks proxy '
              'of your browser to localhost:{0} and open this url - {1}'
              .format(SOCKS_PORT, cm_url))

    def __init__(self, prompter=None, config_writer=None):
        super(SocksProxyCommand, self).__init__()
        self.is_hidden = False
        self._operation_callers = []
