"""
hudai.helpers.http_client
"""

from datetime import date, datetime
from pydash.chaining import chain
from pydash.objects import map_values
from pydash.strings import camel_case, snake_case
import requests

from .. import __version__

USER_AGENT = 'HUD.ai Python v{version} +({docs})'.format(
    version=__version__,
    docs='https://github.com/FoundryAI/hud-ai-python#readme'
)


class HttpClient(object):
    """
    HTTP client based on `requests` with added convenicenes
        - serializes, deserializes JSON
        - adds auth headers from HudAiClient
    """

    def __init__(self, hud_client, base_url):
        self._hud_client = hud_client
        self._base_url = base_url

    def http_get(self, path, query_params={}, refresh_tokens=True):
        """
        Wrapped HTTP action that
            - translates Python objects to JSON objects
            - injects the required headers
            - translates the API response back into a Pythonic form
        """
        response = requests.get(self._build_url(path),
                                params=_jsonify(query_params),
                                headers=self._get_headers(refresh_tokens))

        return _pythonify(response.json())

    def http_post(self, path, query_params={}, data={}, refresh_tokens=True):
        """
        Wrapped HTTP action that
            - translates Python objects to JSON objects
            - injects the required headers
            - translates the API response back into a Pythonic form
        """
        response = requests.post(self._build_url(path),
                                 params=_jsonify(query_params),
                                 json=_jsonify(data),
                                 headers=self._get_headers(refresh_tokens))

        return _pythonify(response.json())

    def http_put(self, path, query_params={}, data={}, refresh_tokens=True):
        """
        Wrapped HTTP action that
            - translates Python objects to JSON objects
            - injects the required headers
            - translates the API response back into a Pythonic form
        """
        response = requests.put(self._build_url(path),
                                params=_jsonify(query_params),
                                json=_jsonify(data),
                                headers=self._get_headers(refresh_tokens))

        return _pythonify(response.json())

    def http_patch(self, path, query_params={}, data={}, refresh_tokens=True):
        """
        Wrapped HTTP action that
            - translates Python objects to JSON objects
            - injects the required headers
            - translates the API response back into a Pythonic form
        """
        response = requests.patch(self._build_url(path),
                                  params=_jsonify(query_params),
                                  json=_jsonify(data),
                                  headers=self._get_headers(refresh_tokens))

        return _pythonify(response.json())

    def http_delete(self, path, query_params={}, refresh_tokens=True):
        """
        Wrapped HTTP action that
            - translates Python objects to JSON objects
            - injects the required headers
            - translates the API response back into a Pythonic form
        """
        response = requests.delete(self._build_url(path),
                                   params=_jsonify(query_params),
                                   headers=self._get_headers(refresh_tokens))

        return _pythonify(response.json())

    # Private

    def _build_url(self, path):
        return '{}{}'.format(self._base_url, path)

    def _get_headers(self, refresh_tokens=True):
        headers = {'User-Agent': USER_AGENT}

        if refresh_tokens:
            self._hud_client.refresh_tokens()

        token = self._hud_client.access_token
        if token:
            headers['Authorization'] = 'Bearer {token}'.format(token=token)

        return headers


def _jsonify(value):
    if not isinstance(value, dict):
        return _web_safe(value)

    return chain(value) \
        .map_keys(lambda value, key: camel_case(key)) \
        .map_values(lambda value: _jsonify(value)) \
        .value()

def _pythonify(value):
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            return value

    if isinstance(value, list):
        return [_pythonify(item) for item in value]

    if isinstance(value, dict):
        return chain(value) \
            .map_keys(lambda value, key: snake_case(key)) \
            .map_values(lambda value: _pythonify(value)) \
            .value()

    return value

def _web_safe(value):
    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, list):
        return [_web_safe(item) for item in value]

    if isinstance(value, dict):
        return map_values(value, lambda element: _web_safe(element))

    return value
