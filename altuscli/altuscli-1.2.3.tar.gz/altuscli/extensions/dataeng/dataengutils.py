# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from altuscli import exceptions


def get_cm_endpoint(cluster, cluster_name):
    if 'status' in cluster:
        cluster_status = cluster['status']
    else:
        raise exceptions.ClusterStatusNotFound(cluster_name=cluster_name)

    status_to_exception = {
        'CREATING': exceptions.ClusterStartingError,
        'TERMINATING': exceptions.ClusterTerminatingError,
        'FAILED': exceptions.ClusterFailedError
    }

    if cluster_status in status_to_exception:
        raise status_to_exception.get(cluster_status)(cluster_name=cluster_name)

    if 'clouderaManagerEndpoint' in cluster:
        return cluster['clouderaManagerEndpoint']

    raise exceptions.ClusterEndpointNotFound(cluster_name=cluster_name)


def get_cluster(client_creator, parsed_globals, cluster_name):
    client = get_client(client_creator, parsed_globals)
    return client.describe_cluster(clusterName=cluster_name)['cluster']


def get_client(client_creator, parsed_globals):
    return client_creator.create_client(
        'dataeng',
        parsed_globals.endpoint_url,
        parsed_globals.verify_tls,
        client_creator.context.get_credentials())
