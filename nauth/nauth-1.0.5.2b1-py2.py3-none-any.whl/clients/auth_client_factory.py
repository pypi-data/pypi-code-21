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

from nauth.clients.auth0_client import Auth0Client
from nauth.clients.uaa_client import UaaClient


def get_auth_client(auth_client_config):
    auth_clients = {
        "cloud": Auth0Client,
        "cloudless": UaaClient,
    }
    auth_type = auth_client_config.auth_type
    auth_client_class = auth_clients.get(auth_type, Auth0Client)
    return auth_client_class(auth_client_config)
