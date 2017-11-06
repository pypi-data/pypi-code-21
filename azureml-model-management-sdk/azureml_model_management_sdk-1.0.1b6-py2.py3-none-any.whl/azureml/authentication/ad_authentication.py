# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-


class ADAuthentication(object):

    def __init__(self, http_client):
        self._http_client = http_client

    def acquire_token(self, username, password):
        req = {'username': username, 'password': password}
        return self._http_client.post('/login', json=req).json()['access_token']
