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

from .apiclient import ApiClient


class Base(ApiClient):
    def info(self, **kwargs) -> dict():
        """
        Returns key characteristics of the API such as the server name and the
        default version.

        Returns:
            dict:
                - url
                - version
        """
        return self.get_json('/', **kwargs)

    def me(self, **kwargs) -> dict():
        """
        Returns information on the logged in user.

        The current user is either the auth_user or, if provided, the run_as
        user.

        Returns:
            dict:
                - email
                - name
                - provider
                - userrole
                - username
        """
        return self.get_json('/info/me', **kwargs)

    def me_roles(self, **kwargs) -> list():
        """
        Returns current user's roles.

        Returns:
            list: user's roles
        """
        return self.get_json('/info/me/roles', **kwargs)

    def organization(self, **kwargs) -> dict():
        """
        Returns the current organization.

        Returns:
            dict:
                - adminRole
                - anonymousRole
                - id
                - name
        """
        return self.get_json('/info/organization', **kwargs)

    def organization_properties(self, **kwargs) -> dict():
        """
        Returns the current organization's properties.

        Returns:
            dict: organization's properties
        """
        return self.get_json('/info/organization/properties', **kwargs)
