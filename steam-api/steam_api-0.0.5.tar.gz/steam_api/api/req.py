from .const import *
from .. import error
import requests


class SteamApiRequest:
    """
    Http Request Wrapper using `requests`
    """
    def __init__(self):
        pass

    @staticmethod
    def get(endpoint, path, version, payload=None):
        """
        using http method 'GET'

        :param endpoint: NEWS_ENDPOINT, PLAYER_ENDPOINT, USER_ENDPOINT
        :param path: url path
        :param version: v0001, v0002
        :param payload: params
        :return: requests object
        """
        url = '{domain}{endpoint}{path}/{version}'.format(
            domain=STEAM_API_URL,
            endpoint=endpoint,
            path=path,
            version=version,
        )

        response = requests.get(url, params=payload)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            error.handle_error(response)

    def post(self):
        """
        todo
        using http method 'POST'

        :return:
        """
        pass
