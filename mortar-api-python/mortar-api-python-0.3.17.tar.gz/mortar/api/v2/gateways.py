#
# Copyright 2014 Mortar Data Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from requests.exceptions import HTTPError

def get_gateway(api):
    """
    Get currently running gateway.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs 
    
    :rtype: dict
    :returns: currently running gateway, or None if no gateway running
    """
    try:
        return api.get('gateways')
    except HTTPError, e:
        if e.response and e.response.status_code == 404:
            return None
        else:
            raise
