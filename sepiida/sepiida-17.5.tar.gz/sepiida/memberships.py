import logging
import urllib.parse

import requests

import sepiida.environment
from sepiida.requests import privileged_session, user_session

LOGGER = logging.getLogger(__name__)

class MembershipsBadRequestError(Exception):
    pass

class MembershipsUnauthorizedError(Exception):
    pass

class MembershipsForbiddenError(Exception):
    pass

class MembershipsNotFoundError(Exception):
    pass

class MembershipsRequestError(Exception):
    pass

class MembershipsConnectionError(Exception):
    pass

class MembershipsPaoRootError(Exception):
    pass

def is_privileged():
    return is_privileged.nest > 0
is_privileged.nest = 0

def _send_request(http_method, uri=None, query=None, payload=None, timeout=10, privileged=False):
    privileged = is_privileged() or privileged
    pao_root = sepiida.environment.get().USER_SERVICE
    url = uri or urllib.parse.urljoin(pao_root, '/memberships/')

    session = privileged_session() if privileged else user_session()
    try:
        if query:
            response = session.request(http_method, url, data=query, timeout=timeout)
        else:
            response = session.request(http_method, url, json=payload, timeout=timeout)
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
        raise MembershipsConnectionError(e)

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
            raise MembershipsBadRequestError(message)
        elif response.status_code == 401:
            raise MembershipsUnauthorizedError(message)
        elif response.status_code == 403:
            raise MembershipsForbiddenError(message)
        elif response.status_code == 404:
            raise MembershipsNotFoundError(message)
        else:
            raise MembershipsRequestError(message)

    return response

def _payload(group, user):
    return {
        'group'     : group,
        'user'      : user,
    }

def create(group, user, privileged=False):
    http_method = 'POST'
    payload = _payload(group, user)
    response = _send_request(http_method, payload=payload, privileged=privileged)
    return response.headers['Location']

def delete(uri, privileged=False):
    http_method = 'DELETE'
    response = _send_request(http_method, uri=uri, privileged=privileged)
    assert response.status_code == 204

def get(uri=None, privileged=False):
    http_method = 'GET'
    response = _send_request(http_method, uri=uri, privileged=privileged)
    return response.json()

def search(group=None, user=None, privileged=False):
    http_method = 'GET'
    filters = []
    if group:
        filters.append("filter[group]={}".format(group))
    if user:
        filters.append("filter[user]={}".format(user))
    filters_qs = "&".join(filters)
    response = _send_request(http_method, query=filters_qs, privileged=privileged)
    return response.json()['resources']
