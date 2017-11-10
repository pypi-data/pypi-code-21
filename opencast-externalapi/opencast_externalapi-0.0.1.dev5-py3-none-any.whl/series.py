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

import uuid

from .apiclient import ApiClient


class Series(ApiClient):
    def get_series(self, filter=None, **kwargs) -> dict():
        parameters = {}
        # TODO: validate filter
        if filter:
            parameters['filter'] = filter

        return self.get_json('/series', parameters=parameters, **kwargs)

    def create_series(self, metadata, acl, theme=None, **kwargs) -> str():
        data = {
            'metadata': metadata,
            'acl': acl,
        }
        if theme:
            data['theme'] = theme

        r = self.req('/series', method='POST', data=data, **kwargs)

        identifier = r.json().get('identifier')
        return uuid.UUID(identifier)
