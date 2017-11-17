# Copyright (c) 2017 Qumulo, Inc.
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
import qumulo.lib.util as util

@request.request
def settings_set(
        conninfo, credentials, bind_uri, base_dn, ldap_schema='RFC2307',
        user='', password='', gids_extension=False,
        encrypt_connection = True):

    method = "PUT"
    uri = '/v1/ldap/settings'

    settings = {
        "bind_uri":           util.parse_ascii(bind_uri, 'bind_uri'),
        "base_dn":            util.parse_ascii(base_dn, 'base_dn'),
        "ldap_schema":        util.parse_ascii(ldap_schema, 'ldap_schema'),
        "user":               util.parse_ascii(user, 'user'),
        "gids_extension":     gids_extension,
        "encrypt_connection": encrypt_connection,
    }
    if password != None:
        settings["password"] = util.parse_ascii(password, 'password')

    return request.rest_request(
        conninfo, credentials, method, uri, body=settings)

@request.request
def settings_get(conninfo, credentials):
    method = "GET"
    uri = '/v1/ldap/settings'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def settings_update(
    conninfo, credentials, bind_uri=None, base_dn=None, ldap_schema=None,
    user=None, password=None, gids_extension=None,
    encrypt_connection=None):
    method = "PATCH"
    uri = '/v1/ldap/settings'

    settings = {}

    if bind_uri != None:
        settings['bind_uri'] = bind_uri
    if base_dn != None:
        settings['base_dn'] = base_dn
    if ldap_schema != None:
        settings['ldap_schema'] = ldap_schema
    if user != None:
        settings['user'] = user
    if password != None:
        settings['password'] = password
    if gids_extension != None:
        settings['gids_extension'] = gids_extension
    if encrypt_connection != None:
        settings['encrypt_connection'] = encrypt_connection

    return request.rest_request(
        conninfo, credentials, method, uri, body=settings)

@request.request
def uid_number_to_uid_get(conninfo, credentials, uid_number):
    method = "GET"
    uri = "/v1/ldap/uid-number/" + str(uid_number) + "/uid"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def uid_to_gid_numbers_get(conninfo, credentials, uid):
    method = "GET"
    uri = "/v1/ldap/uid/" + str(uid) + "/gids"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def uid_to_uid_number_get(conninfo, credentials, uid):
    method = "GET"
    uri = "/v1/ldap/uid/" + str(uid) + "/uid-number"

    return request.rest_request(conninfo, credentials, method, uri)
