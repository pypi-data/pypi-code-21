import logging
import urllib.parse

import sepiida.environment
from sepiida.requests import privileged_session
from sepiida.session import current_user_uri

LOGGER = logging.getLogger(__name__)

def search():
    session = privileged_session()
    settings = sepiida.environment.get()
    url = urllib.parse.urljoin(settings.USER_SERVICE, '/memberships/?filter[user]={}'.format(current_user_uri()))
    response = session.request('GET', url)

    if not response.ok:
        LOGGER.error('Error sending request GET %s: %s %s',
            url,
            response.status_code,
            response.text,
        )
        raise Exception('Failed Request, Response: {}, {}'.format(response.status_code, response.text))
    return response.json()

def has_any(group_names):
    memberships = search()['resources']
    session = privileged_session()
    settings = sepiida.environment.get()
    url = urllib.parse.urljoin(settings.USER_SERVICE, '/groups/?filter[name]={}'.format(','.join(group_names)))
    response = session.request('GET', url)

    if not response.ok:
        LOGGER.error('Error sending request GET %s: %s %s',
            url,
            response.status_code,
            response.text,
        )
        raise Exception('Failed Request, Response: {}, {}'.format(response.status_code, response.text))

    groups = [group['uri'] for group in response.json()['resources']]

    for membership in memberships:
        if membership['group'] in groups:
            return True
    return False
