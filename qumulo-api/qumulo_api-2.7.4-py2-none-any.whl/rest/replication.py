# Copyright (c) 2016 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import qumulo.lib.request as request

@request.request
def replicate(conninfo, credentials, relationship):
    method = "POST"
    uri = "/v1/replication/source-relationships/{}/replicate".format(
        relationship)
    return request.rest_request(
        conninfo, credentials, method, unicode(uri))

@request.request
def create_source_relationship(
        conninfo,
        credentials,
        source,
        target_path,
        address,
        disable_continuous_replication=False,
        target_port=None):

    body = {'source_root_id': source,
            'target_root_path': target_path,
            'target_address': address,
            'continuous_replication_enabled':
                not disable_continuous_replication}
    if target_port:
        body['target_port'] = target_port

    method = "POST"
    uri = "/v1/replication/source-relationships/"
    return request.rest_request(conninfo, credentials, method, uri, body=body)

@request.request
def list_source_relationships(conninfo, credentials):
    method = "GET"
    uri = "/v1/replication/source-relationships/"
    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_source_relationship(conninfo, credentials, relationship_id):
    method = "GET"
    uri = "/v1/replication/source-relationships/{}"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def delete_source_relationship(conninfo, credentials, relationship_id):
    method = "DELETE"
    uri = "/v1/replication/source-relationships/{}"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def delete_target_relationship(conninfo, credentials, relationship_id):
    method = "POST"
    uri = "/v1/replication/target-relationships/{}/delete"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def modify_source_relationship(
        conninfo, credentials,
        relationship_id,
        new_target_address=None,
        new_target_port=None,
        continuous_replication_enabled=None,
        blackout_windows=None,
        blackout_window_timezone=None,
        etag=None):

    method = "PATCH"
    uri = "/v1/replication/source-relationships/{}"

    body = {}
    if new_target_address is not None:
        body['target_address'] = new_target_address
    if new_target_port is not None:
        body['target_port'] = new_target_port
    if continuous_replication_enabled is not None:
        body['continuous_replication_enabled'] = continuous_replication_enabled
    if blackout_windows is not None:
        body['blackout_windows'] = blackout_windows
    if blackout_window_timezone is not None:
        body['blackout_window_timezone'] = blackout_window_timezone

    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id), body=body,
        if_match=etag)

@request.request
def list_source_relationship_statuses(conninfo, credentials):
    method = "GET"
    uri = "/v1/replication/source-relationships/status/"
    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def list_target_relationship_statuses(conninfo, credentials):
    method = "GET"
    uri = "/v1/replication/target-relationships/status/"
    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_source_relationship_status(conninfo, credentials, relationship_id):
    method = "GET"
    uri = "/v1/replication/source-relationships/{}/status"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def get_target_relationship_status(conninfo, credentials, relationship_id):
    method = "GET"
    uri = "/v1/replication/target-relationships/{}/status"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def authorize(conninfo, credentials, relationship_id):
    method = "POST"
    uri = "/v1/replication/target-relationships/{}/authorize"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def abort_replication(conninfo, credentials, relationship_id):
    method = "POST"
    uri = "/v1/replication/source-relationships/{}/abort-replication"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))
