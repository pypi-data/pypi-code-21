import sys
import urllib2

from functools import partial
from multiprocessing.pool import ThreadPool


class Feed(object):
    @staticmethod
    def _request(url, headers=None):
        request = urllib2.Request(url)
        if headers is not None:
            for key, value in headers.items():
                request.add_header(key, value)

        return urllib2.urlopen(request)

    def _request_in_pool(self, urls, headers=None):
        pool = ThreadPool(15)
        request_func = partial(self._request, headers=headers)

        return pool.map(request_func, urls)
