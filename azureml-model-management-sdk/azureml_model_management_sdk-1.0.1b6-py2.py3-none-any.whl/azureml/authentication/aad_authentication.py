# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

import adal


class AADAuthentication(object):
    """Azure Active Directory authentication handling"""

    def __init__(self, options):
        self.options = options
        self._raise_errors(['authuri', 'tenant', 'resource', 'clientid'])

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def acquire_token(self):
        opts = self.options
        authuri = opts['authuri']
        tenant = opts['tenant']
        resource = opts['resource']
        clientid = opts['clientid']

        ctx = adal.AuthenticationContext(authuri + '/' + tenant, api_version=None)

        if 'username' in opts:
            # --- acquire_token_with_username_password ---

            self._raise_errors(['password'])
            token = ctx.acquire_token_with_username_password(
                resource,
                opts['username'],
                opts['password'],
                clientid)

        elif 'code' in opts:
            # --- acquire_token_with_device_code with existing `code` ---

            code = opts['code']
            token = ctx.acquire_token_with_device_code(resource, code, clientid)

        else:
            # --- acquire_token_with_device_code (no `code`) ---
            # if a callback hoos is provided by the user
            # use the callback hook otherwise we will continue to block until
            # the uer-code is applied
            # otherwise, print the link and wait for user's action

            code = ctx.acquire_user_code(resource, clientid)
            if 'user_code_callback' in opts:
                opts['user_code_callback'](code)
            else:
                print(code['message'])

            token = ctx.acquire_token_with_device_code(resource, code, clientid)

        if 'accessToken' not in token:
            msg = 'Failed to acquire an access token with:\n' \
                  '   authuri: {authuri}\n' \
                  '    tenant: {tenant}\n' \
                  '  clientid: {clientid}\n' \
                  '  resource: {resource}'.format(opts)
            raise ValueError(msg)

        return token['accessToken']

    def _raise_errors(self, required=[]):
        missing = []

        for key in required:
            if key not in self.options:
                missing.append('A valid `{0}` is required.'.formate(key))

        if len(missing) > 0:
            raise ValueError('\n'.join(missing))
