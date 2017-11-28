# coding: utf-8
import requests
from bs4 import BeautifulSoup


class AuthException(Exception):
    pass


def get_django_client(login_url, username, password):
    client = requests.session()
    response = client.get(login_url)
    cookies = response.cookies

    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_input = soup.find(attrs={'name': 'csrfmiddlewaretoken'})
    csrf_token = csrf_input['value']

    params = {
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': csrf_token,
    }
    response = client.post(login_url, params, cookies=cookies, headers={'Referer': login_url})

    if response.status_code != 200:
        raise AuthException('Status code: %s' % response.status_code)

    return client
