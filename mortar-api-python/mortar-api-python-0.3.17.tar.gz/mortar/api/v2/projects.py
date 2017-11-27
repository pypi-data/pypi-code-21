#
# Copyright 2013 Mortar Data Inc.
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

# project statuses
PROJECT_STATUS_PENDING    = "PENDING"
PROJECT_STATUS_CREATING   = "CREATING"
PROJECT_STATUS_ACTIVE     = "ACTIVE"
PROJECT_STATUS_FAILED     = "FAILED"
PROJECT_STATUS_DELETED    = "DELETED"

# statuses that indicate a project is done with creation
STATUSES_COMPLETE = [PROJECT_STATUS_ACTIVE, PROJECT_STATUS_FAILED]

def get_projects(api):
    """
    Get all active Mortar projects for logged-in user.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs
    
    :rtype: list:
    :returns: list of dict with details on projects
    """
    return api.get('projects')

def get_project(api, project_id):
    """
    Get a Mortar project for logged-in user.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API
    
    :type project_id: str
    :param project_id: ID of project (or project name also accepted)
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs
    
    :rtype: dict:
    :returns: dictionary with project details
    """
    return api.get('projects/%s' % project_id)

def post_project(api, project_name):
    """
    Create a new project.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type project_name: str
    :param project_name: Name of new Mortar project
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs
    
    :rtype: dict:
    :returns: dict with details for newly created project
    """
    
    body = {'project_name': project_name}
    return api.post('projects', body)

def delete_project(api, project_id):
    """
    Delete a Mortar projct.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type project_id: str
    :param project_id: ID (or project name) of project to delete
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs    
    """
    return api.delete('projects/%s' % project_id)
