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

from mortar.api.v2 import jobs

import mock

class TestJobs(unittest.TestCase):

    def setUp(self):
        self.api_mock = mock.Mock()
        self.project_name = 'my_project'
        self.script_name = 'my_script'

    def test_get_script_name_key(self):
        for job_type, expected_key in (
            ('spark-on-jobserver', 'sparkclass'),
            ('spark', 'sparkclass'),
            ('luigi', 'luigiscript'),
            ('pig', 'pigscript'),
            ('unrecognized-type', 'pigscript'),
        ):
            expected_result = '{0}_name'.format(expected_key)
            self.assertEqual(jobs.get_script_name_key(job_type), expected_result)

    def test_post_job_new_cluster(self):
        cluster_size = 2
        expected_job_id = 'abcdefghijklmnop'
        self.api_mock.post.return_value = {'job_id': expected_job_id}
        actual_job_id = jobs.post_job_new_cluster(self.api_mock, self.project_name, self.script_name, cluster_size)
        self.assertEquals(expected_job_id, actual_job_id)

    def test_post_job_new_cluster_with_pipeline_job_id(self):
        cluster_size = 2
        expected_job_id = 'abcdefghijklmnop'
        pipeline_job_id = '10d83d8kfd8k38sf'
        self.api_mock.post.return_value = {'job_id': expected_job_id}
        actual_job_id = jobs.post_job_new_cluster(self.api_mock, self.project_name, self.script_name, cluster_size,
                                                  pipeline_job_id=pipeline_job_id)
        self.assertEquals(expected_job_id, actual_job_id)

    def test_post_job_new_cluster_with_emr_release_label(self):
        cluster_size = 2
        expected_job_id = 'abcdefghijklmnop'
        emr_release_label = 'some.version'
        self.api_mock.post.return_value = {'job_id': expected_job_id}
        actual_job_id = jobs.post_job_new_cluster(self.api_mock, self.project_name, self.script_name, cluster_size,
                                                  emr_release_label=emr_release_label)
        self.assertEquals(expected_job_id, actual_job_id)

    def test_post_web_job_new_cluster(self):
        cluster_size = 2
        expected_job_id = 'abcdefghijklmnop'
        self.api_mock.post.return_value = {'job_id': expected_job_id}
        actual_job_id = jobs.post_web_job_new_cluster(self.api_mock, self.script_name, cluster_size)
        self.assertEquals(expected_job_id, actual_job_id)

    def test_post_job_existing_cluster(self):
        cluster_id = 'xyz123fdsa'
        expected_job_id = 'abcdefghijklmnop'
        self.api_mock.post.return_value = {'job_id': expected_job_id}
        actual_job_id = jobs.post_job_new_cluster(self.api_mock, self.project_name, self.script_name, cluster_id)
        self.assertEquals(expected_job_id, actual_job_id)

    def test_post_job_existing_cluster_with_pipeline_job_id(self):
        cluster_id = 'xyz123fdsa'
        expected_job_id = 'abcdefghijklmnop'
        pipeline_job_id = '10d83d8kfd8k38sf'
        self.api_mock.post.return_value = {'job_id': expected_job_id}
        actual_job_id = jobs.post_job_new_cluster(self.api_mock, self.project_name, self.script_name, cluster_id, 
            pipeline_job_id=pipeline_job_id)
        self.assertEquals(expected_job_id, actual_job_id)

    def test_post_job_existing_cluster_with_emr_release_label(self):
        cluster_id = 'xyz123fdsa'
        expected_job_id = 'abcdefghijklmnop'
        emr_release_label = 'some.version'
        self.api_mock.post.return_value = {'job_id': expected_job_id}
        actual_job_id = jobs.post_job_new_cluster(self.api_mock, self.project_name, self.script_name, cluster_id,
                                                  emr_release_label=emr_release_label)
        self.assertEquals(expected_job_id, actual_job_id)

    def test_post_web_job_existing_cluster(self):
        cluster_id = 'xyz123fdsa'
        expected_job_id = 'abcdefghijklmnop'
        self.api_mock.post.return_value = {'job_id': expected_job_id}
        actual_job_id = jobs.post_web_job_new_cluster(self.api_mock, self.script_name, cluster_id)
        self.assertEquals(expected_job_id, actual_job_id)

    def test_get_job(self):
        job_id = 'xyz'
        response = {'job_id': job_id, 'status_code': 'success'}
        self.api_mock.get.return_value = response
        job = jobs.get_job(self.api_mock, job_id)
        self.assertEquals(job, response)

    def test_get_jobs(self):
        response = [{'job_id': 'abc', 'status_code': 'success'},
                    {'job_id': 'xyz', 'status_code': 'success'}]
        self.api_mock.get.return_value = response
        return_jobs = jobs.get_jobs(self.api_mock)
        self.assertEquals(return_jobs, response)

    def test_post_spark_job_existing_cluster(self):
        cluster_id = 'xyz123fdsa'
        expected_job_id = 'abcdefghijklmnop'
        self.api_mock.post.return_value = {'job_id': expected_job_id}
        actual_job_id = jobs.post_job_existing_cluster(self.api_mock, self.project_name, self.script_name, cluster_id,
            job_type=jobs.JOB_TYPE_SPARK_ON_JOBSERVER)
        self.assertEquals(expected_job_id, actual_job_id)

    def test_post_job_existing_cluster_with_use_vpc_for_emr(self):
        cluster_id = 'xyz123fdsa'
        expected_job_id = 'abcdefghijklmnop'
        emr_release_label = 'some.version'
        self.api_mock.post.return_value = {'job_id': expected_job_id}
        actual_job_id = jobs.post_job_new_cluster(self.api_mock, self.project_name, self.script_name, cluster_id,
                                                  use_vpc_for_emr=True)
        self.assertEquals(expected_job_id, actual_job_id)