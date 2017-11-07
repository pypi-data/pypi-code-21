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

# cluster status_code values
CLUSTER_STATUS_PENDING    = "pending"
CLUSTER_STATUS_STARTING   = "starting"
CLUSTER_STATUS_STARTING_REQUESTED_STOP = "starting_requested_stop"
CLUSTER_STATUS_RUNNING    = "running"
CLUSTER_STATUS_STOPPING   = "stopping"
CLUSTER_STATUS_DESTROYED  = "destroyed"
CLUSTER_STATUS_FAILED     = "failed"

# cluster types
CLUSTER_TYPE_SINGLE_JOB = 'single_job'
CLUSTER_TYPE_PERSISTENT = 'persistent'
CLUSTER_TYPE_PERMANENT  = 'permanent'

# Local cluster id
LOCAL_CLUSTER_ID = "local"

CLUSTER_BACKEND__EMR_HADOOP_1 = "EMR_HADOOP_1"
CLUSTER_BACKEND__EMR_HADOOP_2 = "EMR_HADOOP_2"
CLUSTER_BACKEND__EMR_HADOOP_2_7_3 = "EMR_HADOOP_2_7_3"
CLUSTER_BACKEND__EMR_SPARK_JOBSERVER = "EMR_SPARK_JOBSERVER"
CLUSTER_BACKEND__ALL          = "ALL"


def get_clusters(api, params=None):
    """
    Get recent and running clusters.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs
    
    :rtype: dict:
    :returns: running and recent clusters
    """
    return api.get('clusters', params)

def stop_cluster(api, cluster_id):
    """
    Stop a running cluster.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type cluster_id: str
    :param cluster_id: cluster to stop
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs    
    """
    api.delete('clusters/%s' % cluster_id)
