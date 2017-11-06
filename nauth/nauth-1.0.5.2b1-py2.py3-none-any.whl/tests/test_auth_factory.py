# ----------------------------------------------------------------------------
# Copyright 2015-2017 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
#
# # -*- coding: utf-8 -*-

from nauth.clients.auth_client import AuthClientConfig
from nauth.clients import auth_client_factory
from nauth.clients.auth0_client import Auth0Client


def test_default_client_is_auth0():
    """
    get_auth_client() when auth_type is not set should return Auth0Client
    """
    auth_config = AuthClientConfig()
    auth_client = auth_client_factory.get_auth_client(auth_config)

    assert isinstance(auth_client, Auth0Client)
