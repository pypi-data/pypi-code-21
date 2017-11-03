#!/usr/bin/env python

import requests

from .utils import get_user_agent
from .decorators import singleton


@singleton
class Downloader(object):

    TIMEOUT = 5

    def __init__(self, user_agent=None, timeout=None):
        self._useragent = user_agent or get_user_agent()
        self._timeout = timeout or self.TIMEOUT
        self._cache = {}

    def __call__(self, url):
        result = None
        if self._cache:
            if url in self._cache.keys():
                result = self._cache[url]

        if result is None:
            r = self.download(url)
            if r.status_code == 200:
                self._cache[url] = r.content
                return r.content
            else:
                return None

        return self._cache[url]

    def download(self, url):
        headers = requests.utils.default_headers()
        headers.update({'User-Agent': self._useragent})

        r = requests.get(url, headers=headers, timeout=self._timeout)

        return r

    def delay(self):
        pass
