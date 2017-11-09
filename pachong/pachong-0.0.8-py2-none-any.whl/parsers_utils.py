#-*-coding:utf-8-*-
__author__ = 'cchen'

import re
from urlparse import urlsplit, parse_qsl


def parse_url_args(url):
    return dict(parse_qsl(urlsplit(url).query))


def keep_int(text):
    return re.sub('[^0-9]', '', text)


def get_url(url, with_query=True):
    url = ('https:' if url.startswith('//') else '') + url
    if not with_query:
        url = url.split('?', 1)[0]
    return url
