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

import time

from mortar.api.v2 import clusters

# Job Status constants
STATUS_STARTING          = 'starting'
STATUS_GATEWAY_STARTING  = 'GATEWAY_STARTING' #Comes from task.
STATUS_VALIDATING_SCRIPT = 'validating_script'
STATUS_SCRIPT_ERROR      = 'script_error'
STATUS_PLAN_ERROR        = 'plan_error'
STATUS_STARTING_CLUSTER  = 'starting_cluster'
STATUS_RUNNING           = 'running'
STATUS_SUCCESS           = 'success'
STATUS_FINISHED          = 'finished'
STATUS_EXECUTION_ERROR   = 'execution_error'
STATUS_COMPILATION_ERROR = 'compilation_error'
STATUS_SERVICE_ERROR     = 'service_error'
STATUS_STOPPING          = 'stopping'
STATUS_STOPPED           = 'stopped'

# All statuses that indicate a completed job
COMPLETE_STATUSES = (
    STATUS_SCRIPT_ERROR,
    STATUS_PLAN_ERROR,
    STATUS_SUCCESS,
    STATUS_EXECUTION_ERROR,
    STATUS_COMPILATION_ERROR,
    STATUS_SERVICE_ERROR,
    STATUS_STOPPED,
    STATUS_FINISHED)

JOB_TYPE_PIG   = 'pig'
JOB_TYPE_LUIGI = 'luigi'
JOB_TYPE_SPARK = 'spark'
JOB_TYPE_SPARK_ON_JOBSERVER = 'spark-on-jobserver'

PIG__0_12 = "0.12"
PIG__0_12_HADOOP_2 = "0.12-Hadoop-2"
PIG__0_12_HADOOP_2_7_3 = "0.12-Hadoop-2.7.3"


def get_script_name_key(job_type):
    """
    internal DRY helper for common API parameter.
    """
    if job_type in (JOB_TYPE_SPARK_ON_JOBSERVER, JOB_TYPE_SPARK):
        return 'sparkclass_name'
    elif job_type == JOB_TYPE_LUIGI:
        return 'luigiscript_name'
    else:
        # default is to assume pig.
        return 'pigscript_name'


def post_job_new_cluster(api, project_name, script_name, cluster_size, cluster_type=clusters.CLUSTER_TYPE_PERSISTENT,
                         git_ref='master', parameters=None, notify_on_job_finish=True, is_control_script=False,
                         pig_version=None, use_spot_instances=True, pipeline_job_id=None, job_type=JOB_TYPE_PIG,
                         cluster_tags=[], instance_type=None, project_build=None, cluster_configuration=None,
                         job_description=None, emr_release_label=None, use_vpc_for_emr=None):
    """
    Post a new job to a new cluster.

    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type project_name: str
    :param project_name: Name of Mortar project where job lives (e.g. myproject)

    :type script_name: str
    :param script_name: Name of pigscript or controlscript to run with no file extension (e.g. mypigscript)

    :type cluster_size: integer
    :param cluster_size: size in number of nodes of new cluster

    :type cluster_type: string
    :param cluster_type: Shutoff policy for cluster: immediately on job completion (single_job), after idle for one hour (persistent), or no automatic shutoff (permanent). Default: persistent.

    :type git_ref: string
    :param git_ref: branch or commit hash at which to run project code.  Default: master.

    :type parameters: dict
    :param parameters: pig parameters to pass to the script

    :type notify_on_job_finish: bool
    :param notify_on_job_finish: whether to send an email when the job finishes. Default: true.

    :type is_control_script: bool
    :param is_control_script: whether the script being run is a controlscript (not a pigscript). Default: false.

    :type pig_version: string
    :param pig_version: Major version of pig to run.  If null, uses the Mortar platform default (currently 0.9).

    :type use_spot_instances: bool
    :param use_spot_instances: whether to launch a cluster using spot instances. Default: true.

    :type pipeline_job_id: string
    :param pipeline_job_id: Luigi pipeline that launched this job, if applicable. Default: None.

    :type job_type: string
    :param job_type: Type of the job. Default: pig.

    :type cluster_tags: list
    :param cluster_tags: Tags that will be assigned to a new cluster.

    :type instance_type: string
    :param instance_type: Instance type for the core nodes of a new cluster.

    :type project_build: string
    :param project_build: ID of the static project build that should be used, either a branch name or a githash.

    :type job_description: string
    :param job_description: Description to be displayed as a hint in Mortar web.

    :type emr_release_label: string
    :param emr_release_label: EMR release label of job (ex. "emr-5.8.0", see http://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html)

    :type use_vpc_for_emr: bool
    :param use_vpc_for_emr: whether to instantiate cluster in VPC or classic

    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs

    :rtype: str:
    :returns: job_id for newly created job
    """
    body = {'project_name': project_name,
            'git_ref': git_ref,
            'cluster_size': cluster_size,
            'instance_type': instance_type,
            'cluster_type': cluster_type,
            'cluster_tags': cluster_tags,
            'parameters': parameters or {},
            'notify_on_job_finish': notify_on_job_finish,
            'use_spot_instances': use_spot_instances,
            'pipeline_job_id': pipeline_job_id,
            'job_type': job_type,
            get_script_name_key(job_type): script_name,
            'project_build': project_build,
            'cluster_configuration': cluster_configuration,
            'job_description': job_description
    }

    if emr_release_label:
        body["emr_release_label"] = emr_release_label

    if use_vpc_for_emr:
        body["use_vpc_for_emr"] = use_vpc_for_emr

    if pig_version:
        body["pig_version"] = pig_version

    return api.post('jobs', body)['job_id']


def post_web_job_new_cluster(api, script_name, cluster_size, cluster_type=clusters.CLUSTER_TYPE_PERSISTENT,
                             parameters=None, notify_on_job_finish=True, pig_version=None, use_spot_instances=True,
                             job_type=JOB_TYPE_PIG, cluster_configuration=None, job_description=None, emr_release_label=None,
                             use_vpc_for_emr=None):
    """
    Post a new job to a new cluster.

    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type script_name: str
    :param script_name: Name of the web project to run (e.g. "My First Web Project")

    :type cluster_size: integer
    :param cluster_size: size in number of nodes of new cluster

    :type cluster_type: string
    :param cluster_type: Shutoff policy for cluster: immediately on job completion (single_job), after idle for one hour (persistent), or no automatic shutoff (permanent). Default: persistent.

    :type parameters: dict
    :param parameters: pig parameters to pass to the script

    :type notify_on_job_finish: bool
    :param notify_on_job_finish: whether to send an email when the job finishes. Default: true.

    :type pig_version: string
    :param pig_version: Major version of pig to run.  If null, uses the Mortar platform default (currently 0.9).

    :type use_spot_instances: bool
    :param use_spot_instances: whether to launch a cluster using spot instances. Default: true.

    :type job_type: string
    :param job_type: Type of the job. Default: pig.

    :type job_description: string
    :param job_description: Description to be displayed as a hint in Mortar web.

    :type emr_release_label: string
    :param emr_release_label: EMR release label of job (ex. "emr-5.8.0", see http://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html)

    :type use_vpc_for_emr: bool
    :param use_vpc_for_emr: whether to instantiate cluster in VPC or classic

    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs

    :rtype: str:
    :returns: job_id for newly created job
    """
    body = {'script_name': script_name,
            'cluster_size': cluster_size,
            'cluster_type': cluster_type,
            'parameters': parameters or {},
            'notify_on_job_finish': notify_on_job_finish,
            'use_spot_instances': use_spot_instances,
            'job_type': job_type,
            get_script_name_key(job_type): script_name,
            'cluster_configuration': cluster_configuration,
            'job_description': job_description
    }

    if emr_release_label:
        body["emr_release_label"] = emr_release_label

    if use_vpc_for_emr:
        body["use_vpc_for_emr"] = use_vpc_for_emr

    if pig_version:
        body["pig_version"] = pig_version

    return api.post('jobs', body)['job_id']



def post_job_existing_cluster(api, project_name, script_name, cluster_id, cluster_type=clusters.CLUSTER_TYPE_PERSISTENT,
                              git_ref='master', parameters=None, notify_on_job_finish=True, is_control_script=False,
                              pig_version=None, pipeline_job_id=None, job_type=JOB_TYPE_PIG, project_build=None,
                              job_description=None, emr_release_label=None, use_vpc_for_emr=None):
    """
    Post a new job to an existing cluster.

    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type project_name: str
    :param project_name: Name of Mortar project where job lives (e.g. myproject)

    :type script_name: str
    :param script_name: Name of pigscript or controlscript to run with no file extension (e.g. mypigscript)

    :type cluster_id: string
    :param cluster_id: ID of cluster on which job should be run.

    :type git_ref: string
    :param git_ref: branch or commit hash at which to run project code.  Default: master.

    :type parameters: dict
    :param parameters: pig parameters to pass to the script

    :type notify_on_job_finish: bool
    :param notify_on_job_finish: whether to send an email when the job finishes. Default: true.

    :type is_control_script: bool
    :param is_control_script: whether the script being run is a controlscript (not a pigscript). Default: false.

    :type pig_version: string
    :param pig_version: Major version of pig to run.  If null, uses the Mortar platform default (currently 0.9).

    :type pipeline_job_id: string
    :param pipeline_job_id: Luigi pipeline that launched this job, if applicable. Default: None.

    :type project_build: string
    :param project_build: ID of the static project build that should be used, either a branch name or a githash.

    :type job_description: string
    :param job_description: Description to be displayed as a hint in Mortar web.

    :type emr_release_label: string
    :param emr_release_label: EMR release label of job (ex. "emr-5.8.0", see http://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html)

    :type use_vpc_for_emr: bool
    :param use_vpc_for_emr: whether to instantiate cluster in VPC or classic

    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs

    :rtype: str:
    :returns: job_id for newly created job
    """
    body = {'project_name': project_name,
            'git_ref': git_ref,
            'cluster_id': cluster_id,
            'parameters': parameters or {},
            'notify_on_job_finish': notify_on_job_finish,
            'pipeline_job_id': pipeline_job_id,
            'job_type': job_type,
            get_script_name_key(job_type): script_name,
            'project_build': project_build,
            'job_description': job_description
    }

    if emr_release_label:
        body["emr_release_label"] = emr_release_label

    if use_vpc_for_emr:
        body["use_vpc_for_emr"] = use_vpc_for_emr

    if pig_version:
        body["pig_version"] = pig_version

    return api.post('jobs', body)['job_id']

def post_web_job_existing_cluster(api, script_name, cluster_id, parameters=None,
                                  notify_on_job_finish=True, pig_version=None, job_type=JOB_TYPE_PIG,
                                  job_description=None, emr_release_label=None, use_vpc_for_emr=None):
    """
    Post a new job to an existing cluster.

    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type script_name: str
    :param script_name: Name of the web project to run (e.g. "My First Web Project")

    :type cluster_id: string
    :param cluster_id: ID of cluster on which job should be run.

    :type parameters: dict
    :param parameters: pig parameters to pass to the script

    :type notify_on_job_finish: bool
    :param notify_on_job_finish: whether to send an email when the job finishes. Default: true.

    :type pig_version: string
    :param pig_version: Major version of pig to run.  If null, uses the Mortar platform default (currently 0.9).

    :type job_description: string
    :param job_description: Description to be displayed as a hint in Mortar web.

    :type emr_release_label: string
    :param emr_release_label: EMR release label of job (ex. "emr-5.8.0", see http://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html)

    :type use_vpc_for_emr: bool
    :param use_vpc_for_emr: whether to instantiate cluster in VPC or classic

    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs

    :rtype: str:
    :returns: job_id for newly created job
    """
    body = {'script_name': script_name,
            'cluster_id': cluster_id,
            'parameters': parameters or {},
            'notify_on_job_finish': notify_on_job_finish,
            'job_type': job_type,
            get_script_name_key(job_type): script_name,
            'job_description': job_description
    }

    if emr_release_label:
        body["emr_release_label"] = emr_release_label

    if use_vpc_for_emr:
        body["use_vpc_for_emr"] = use_vpc_for_emr

    return api.post('jobs', body)['job_id']


def get_job(api, job_id):
    """
    Get job details.

    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type job_id: str
    :param job_id: ID of job

    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs

    :rtype: dict:
    :returns: dictionary with job details
    """
    return api.get('jobs/%s' % job_id)

def get_jobs(api, skip=None, limit=None, search=None, job_type=JOB_TYPE_PIG):
    """
    Get multiple jobs from the API.

    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type skip: integer
    :param skip: Number of jobs in the list (sorted by descending start_timestamp) to skip before returning jobs

    :type limit: integer
    :param limit: Total number of jobs to return at once.

    :type search: dict
    :param search: enables filtering on following keys
                    'luigiscript_name',
                    'pigscript_name',
                    'sparkclass_name',
                    'notes',
                    'pig_status',
                    'luigi_status',
                    'spark_status',
                    'show_pig',
                    'show_spark',
                    'show_luigi'
                    Those values are the only valid keys for the search dict

    :type job_type: str
    :param job_type: 'pig', 'luigi', 'spark' or 'all'

    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs

    :rtype: list:
    :returns: list of dict of job details
    """
    params = {'skip': skip, 'limit': limit, 'job_type': job_type}
    if search:
        for key, val in search.iteritems():
            request_key = 'search[{}]'.format(key)
            params[request_key] = val
    return api.get('jobs', params=params)

def block_until_job_complete(api, job_id, poll_frequency_sec=5.0):
    """
    Block until a job has completed, polling occasionally for status.

    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type job_id: str
    :param job_id: ID of job to poll

    :type poll_frequency_sec: integer
    :param poll_frequency_sec: How frequently to poll.  Default: 5.0 seconds.

    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs

    :rtype: str:
    :returns: final status_code of job
    """

    while True:
        job_status = get_job(api, job_id)['status_code']
        if job_status in COMPLETE_STATUSES:
            return job_status
        time.sleep(poll_frequency_sec)
