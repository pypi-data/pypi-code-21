# Copyright 2017 The WWU eLectures Team All rights reserved.
#
# Licensed under the Educational Community License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/ECL-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import requests
import urllib.parse

logger = logging.getLogger(__name__)

# Supported upstream API version
DEFAULT_API_VERSION = "v1.0.0"


class ApiClient():
    def __init__(self, host, user, password,
                 api_version=DEFAULT_API_VERSION):

        # Account credentials to authenticate with against the API. make sure
        # that this account has the required API_* roles for your desired
        # functions.
        self.auth_user = user
        self.auth_password = password

        # External API uses Basic Auth, which transmits credentials Base64
        # encoded. Using HTTP would transmit passwords in plain text, this
        # is a bad idea.
        if not host.startswith('http'):
            host = 'https://%s' % host
        self.server_url = host
        self.api_version = api_version

    def req(self, path, method='GET', headers={},
            run_as=None,
            run_with_roles=[],
            parameters={},
            sort=None,
            limit=None,
            offset=None,
            **kwargs):

        if sort:
            parameters['sort'] = sort
        if limit:
            parameters['limit'] = limit
        if offset:
            parameters['offset'] = offset
        if run_as:
            headers['X-RUN-AS-USER'] = run_as
        if len(run_with_roles) > 0:
            headers['X-RUN-WITH-ROLES'] = ''.join(run_with_roles, ',')

        headers['Accept'] = 'application/%s+json' % self.api_version

        url = urllib.parse.urljoin(self.server_url, '/api' + path)

        logger.debug(parameters)
        return requests.request(method, url,
                                auth=(self.auth_user, self.auth_password),
                                params=parameters, **kwargs)

    def get_json(self, path, **kwargs):
        r = self.req(path, **kwargs)
        # TODO: define and raise detailed exceptions
        r.raise_for_status()
        return r.json()
