"""
    repo
    ~~~~~~
    Request authenticated user's repos

    :copyright: (c) 2017 by Onni Software Ltd.
    :license: MIT License, see LICENSE for more details

"""

from gease.rest import Api
REPO_URL = 'https://api.github.com/user/repos'


class EndPoint(object):
    """
    Github authenticated user's repo endpoint
    """

    def __init__(self, url=REPO_URL):
        self.__url = url
        self.__client = Api.get_api()

    def get_all_repos(self):
        json_reply = self.__client.get(self.__url)
        return json_reply
