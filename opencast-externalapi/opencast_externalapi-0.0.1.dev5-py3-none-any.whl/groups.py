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


class Groups(ApiClient):

    def get_group(self, group_id=None, **kwargs) -> dict():
        if group_id:
            return self.get_json('/groups/%s' % group_id, **kwargs)
        else:
            return self.get_json('/groups', **kwargs)

    def create_group(self, name, desc="", roles=[], members=[],
                     **kwargs) -> bool():

        roles.append('ROLE_GROUP_%s' % name)

        data = {
            'name': name,
            'description': desc,
            'roles': ','.join(roles),
            'members': ','.join(members),
        }

        r = self.req('/groups', method='POST', data=data, **kwargs)

        return r.status_code == 201

    def delete_group(self, name, **kwargs) -> bool():

        r = self.req('/groups/%s' % name, method='DELETE', **kwargs)

        return r.status_code == 204
