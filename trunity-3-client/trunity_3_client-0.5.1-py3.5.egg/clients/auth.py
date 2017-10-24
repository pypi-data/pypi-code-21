import requests
from requests import Session

from trunity_3_client.utils.url import Url, API_ROOT

__all__ = [
    'get_auth_token',
    'initialize_session',
    'initialize_session_from_creds',
]


def get_auth_token(login, password):
    url = Url(API_ROOT)
    url.tail = 'authorization'

    response = requests.post(url.list, data={
        'login': login,
        'password': password,
    })
    response.raise_for_status()

    content = response.json()
    return content['auth_token']


def initialize_session(auth_token,
                       content_type='multipart/form-data') -> Session:
    session = requests.session()
    session.headers.update({
        'Authorization': auth_token,
        'Accept': 'application/json',
        'Content-Type': content_type,
    })
    return session


def initialize_session_from_creds(login, password,
                                  content_type='multipart/form-data') -> Session:
    auth_token = get_auth_token(login, password)
    return initialize_session(auth_token, content_type)
