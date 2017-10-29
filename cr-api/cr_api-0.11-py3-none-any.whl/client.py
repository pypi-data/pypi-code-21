"""
cr-api client for Clash Royale.
"""
import logging

import requests
from requests.exceptions import HTTPError

from .exceptions import APIError
from .models import Clan, Tag, Player, Constants
from .url import APIURL

logger = logging.getLogger('__name__')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class Client:
    """
    API Client.
    """

    def __init__(self):
        pass

    def fetch(self, url):
        """Fetch URL.

        :param url: URL
        :return: Response in JSON

        """
        try:
            r = requests.get(url)

            if r.status_code != 200:
                logger.error(
                    "API Error | HTTP status {status} | {errmsg} | url: {url}".format(
                        status=resp.status,
                        errmsg=data.get('error'),
                        url=url
                    )
                )
                raise APIError

            data = r.json()

        except HTTPError:
            raise APIError

        except ConnectionError:
            raise APIError

        return data

    def get_clan(self, clan_tag):
        """Fetch a single clan."""
        url = APIURL.clan.format(clan_tag)
        data = self.fetch(url)
        if isinstance(data, list):
            data = data[0]
        return Clan(data=data, url=url)

    def get_clans(self, clan_tags):
        """Fetch multiple clans.

        :param clan_tags: List of clan tags
        """
        url = APIURL.clan.format(','.join(clan_tags))
        data = self.fetch(url)
        return [Clan(data=d, url=url) for d in data]

    def get_top_clans(self):
        """Fetch top clans."""
        data = self.fetch(APIURL.top_clans)
        return data

    def get_profile(self, tag: str) -> Player:
        """Get player profile by tag.
        :param tag:
        :return:
        """
        ptag = Tag(tag).tag
        url = APIURL.profile.format(ptag)
        data = self.fetch(url)
        return Player(data=data, url=url)

    def get_profiles(self, tags):
        """Fetch multiple players from profile API."""
        ptags = [Tag(tag).tag for tag in tags]
        url = APIURL.profile.format(','.join(ptags))
        data = self.fetch(url)
        return [Player(data=d, url=url) for d in data]

    def get_constants(self, key=None):
        """Fetch contants.

        :param key: Optional field.
        """
        url = APIURL.constants
        data = self.fetch(url)
        return Constants(data=data, url=url)
