"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from abc import ABCMeta, abstractmethod
import six
from typing import Dict


@six.add_metaclass(ABCMeta)
class LockingAccountStore(object):
    @abstractmethod
    def lock_account(self, identifier, locked_time):
        # type:(str, int) -> None
        """
        lock this user's account with the specified time
        :param identifier: identifier of a user
        :param locked_time: locked time of the user
        :return:
        """
        pass

    @abstractmethod
    def unlock_account(self, identifier):
        # type: (str) -> None
        """
        unlock the specified user
        :param identifier: identifier of a user
        :return:
        """
        pass


@six.add_metaclass(ABCMeta)
class CredentialsAccountStore(object):
    @abstractmethod
    def get_authc_info(self, identifier):
        # type: (str) -> Dict
        """
        return authenticate information of the specified user
        :param identifier:
        :return:
        """
        pass


@six.add_metaclass(ABCMeta)
class AuthorizationAccountStore(object):
    @abstractmethod
    def get_authz_permissions(self, identifier):
        """
        get all the permissions associated with the specified user
        :param identifier:
        :return:
        """
        pass

    @abstractmethod
    def get_authz_roles(self, identifier):
        """
        get all the roles associated with the specified user
        :param identifier:
        :return:
        """
        pass
