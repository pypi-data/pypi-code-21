import contextlib
import logging
import urllib.parse

import flask
import requests

import sepiida.errors
import sepiida.log
import sepiida.routing
from sepiida.requests import privileged_session, user_session

LOGGER = logging.getLogger(__name__)

CONFIG = {
  'ORIGIN'      : 'sepiida',
  'PAO_ROOT'    : None,
}
def configure(origin, root):
    CONFIG['PAO_ROOT'] = root
    CONFIG['ORIGIN']  = origin

class PermissionsBadRequestError(Exception):
    pass

class PermissionsUnauthorizedError(Exception):
    pass

class PermissionsForbiddenError(Exception):
    pass

class PermissionsNotFoundError(Exception):
    pass

class PermissionsRequestError(Exception):
    pass

class PermissionsConnectionError(Exception):
    pass

class PermissionsPaoRootError(Exception):
    pass

def _send_request(http_method, uri=None, query=None, payload=None, timeout=10, privileged=False):
    privileged = is_privileged() or privileged
    pao_root = CONFIG.get('PAO_ROOT')
    if not pao_root:
        raise PermissionsPaoRootError(
            "You must include a value for PAO_ROOT in your app config,"
            "such as https://pao.service, before querying the permissions system"
        )

    url = uri or urllib.parse.urljoin(pao_root, '/permissions/')

    session = privileged_session() if privileged else user_session()
    try:
        message = "{} {} {}".format(http_method, url, query[:200] + '...' if query and len(query) > 200 else query)
        with sepiida.log.warning_timer(1, message):
            if query:
                response = session.request(http_method, url, data=query, timeout=timeout, headers={'Origin': CONFIG['ORIGIN']})
            else:
                response = session.request(http_method, url, json=payload, timeout=timeout, headers={'Origin': CONFIG['ORIGIN']})
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
        raise PermissionsConnectionError(e)

    if not response.ok:
        LOGGER.debug('Error sending request %s %s with payload %s: %s %s',
            http_method,
            url,
            payload,
            response.status_code,
            response.text,
        )
        message = "Failed Request, Response: {}, {}, Payload: {}".format(response.status_code, response.text, payload)
        if response.status_code == 400:
            raise PermissionsBadRequestError(message)
        elif response.status_code == 401:
            raise PermissionsUnauthorizedError(message)
        elif response.status_code == 403:
            raise PermissionsForbiddenError(message)
        elif response.status_code == 404:
            raise PermissionsNotFoundError(message)
        else:
            raise PermissionsRequestError(message)

    return response

def _payload(object_, holder, right, namespace, resource_name):
    return {
        'holder'        : holder,
        'namespace'     : namespace,
        'object'        : object_,
        'resource_name' : resource_name,
        'right'         : right,
    }

def has_right(object_, right, namespace):
    permissions = search(objects=[object_], rights=[right], namespace=namespace)
    return len(permissions) > 0

def has_any(object_=None, holder=None, right=None, namespace=None):
    permissions = search(
        objects     = [object_] if object_ else None,
        holders     = [holder] if holder else None,
        rights      = [right] if right else None,
        namespace   = namespace if namespace else None,
    )
    return len(permissions) > 0

def get(uri=None, privileged=False):
    http_method = 'GET'
    response = _send_request(http_method, uri=uri, privileged=privileged)
    return response.json()

@contextlib.contextmanager
def always_privileged():
    is_privileged.nest += 1
    try:
        yield
    finally:
        is_privileged.nest -= 1

def is_privileged():
    return is_privileged.nest > 0
is_privileged.nest = 0

def search(fields=None, objects=None, holders=None, rights=None, namespace=None, resource_names=None, privileged=False):
    http_method = 'GET'
    filters = []
    if objects:
        filters.append("filter[object]={}".format(','.join(objects)))
    if holders:
        filters.append("filter[holder]={}".format(','.join(holders)))
    if rights:
        filters.append("filter[right]={}".format(','.join([str(right) for right in rights])))
    if resource_names:
        filters.append("filter[resource_name]={}".format(','.join(resource_names)))
    if namespace:
        filters.append("filter[namespace]={}".format(namespace))
    if fields:
        filters.append("fields=[{}]".format(','.join(fields)))
    filters_qs = "&".join(filters)
    response = _send_request(http_method, query=filters_qs, privileged=privileged)
    return response.json()['resources']

def update_filters(filters, namespace, resource_name, rights=None, app=None):
    """
    Update the provided filters so that permissions for the current user are enforced when querying the database
    The idea here is that pretty much all platform layers will include the ability to filter
    on a particular uuid for a resource. We enforce permissions by limiting their
    query in the database to a list of rows they are allowed to see.
    If the filter already limits to a subset of rows we take the union of the set
    they can see and the set they requested and update the filter accordingly
    This is designed to make it possible to apply filters in a single line
    """
    if is_privileged():
        LOGGER.debug("Refusing to constrain filters because we are currently in an always_privileged context")
        return filters
    uuids = filters.get('uuid', [])
    try:
        objects = [sepiida.routing.uri(resource_name, uuid=u) for u in uuids]
    except sepiida.errors.RoutingError:
        objects = None

    app = app or flask.current_app
    permissions = search(
        fields          = ['resources.object'],
        namespace       = namespace,
        objects         = objects,
        privileged      = False,
        resource_names  = [resource_name],
        rights          = rights,
    )
    resources = [permission['object'] for permission in permissions]
    parameters = [sepiida.routing.extract_parameters(app, 'GET', resource) for resource in resources]
    resource_uuids = {params.get('uuid', params.get('_id')) for endpoint, params in parameters if endpoint == resource_name}
    requested_uuids = filters.get('uuid', None)
    common_uuids = resource_uuids.intersection(requested_uuids) if requested_uuids else resource_uuids
    filters['uuid'] = common_uuids
    return filters

def create(object_, holder, right, namespace, resource_name, privileged=False):
    http_method = 'POST'
    payload = _payload(object_, holder, right, namespace, resource_name)
    response = _send_request(http_method, payload=payload, privileged=privileged)
    return response.headers['Location']

def update(uri, object_, holder, right, namespace, resource_name, privileged=False):
    http_method = 'PUT'
    payload = _payload(object_, holder, right, namespace, resource_name)
    response = _send_request(http_method, uri=uri, payload=payload, privileged=privileged)
    assert response.status_code == 204

def delete(uri, privileged=False):
    http_method = 'DELETE'
    response = _send_request(http_method, uri=uri, privileged=privileged)
    assert response.status_code == 204

def delete_all(objects=None, holders=None, rights=None, namespace=None, privileged=False):
    permissions = search(
        objects   = objects,
        holders   = holders,
        rights    = rights,
        namespace = namespace
    )
    for permission in permissions:
        delete(permission['uri'], privileged=privileged)
