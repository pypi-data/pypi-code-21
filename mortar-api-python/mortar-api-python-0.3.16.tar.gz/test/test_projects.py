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

import unittest

from mortar.api.v2 import projects

import mock

class TestProjects(unittest.TestCase):

    def setUp(self):
        self.api_mock = mock.Mock()
        self.project_name = 'my_project'
    
    def test_post_project(self):
        expected_project = {'project_id': 'abcdefghijklmnop'}
        self.api_mock.post.return_value = expected_project
        actual_project = projects.post_project(self.api_mock, self.project_name)
        self.assertEquals(expected_project, expected_project)

    def test_get_project(self):
        project_id = 'xyz'
        response = {'project_id': project_id, 'name': 'fooproject'}
        self.api_mock.get.return_value = response
        project = projects.get_project(self.api_mock, project_id)
        self.assertEquals(project, response)
    
    def test_get_projects(self):
        response = [{'project_id': 'abc', 'name': 'fooproject'},
                    {'project_id': 'xyz', 'name': 'barproject'}]
        self.api_mock.get.return_value = response
        project = projects.get_projects(self.api_mock)
        self.assertEquals(project, response)

    def test_delete_project(self):
        project_id = 'xyz'
        self.api_mock.delete.return_value = None
        project = projects.delete_project(self.api_mock, project_id)
        self.api_mock.delete.assert_called_with('projects/xyz')