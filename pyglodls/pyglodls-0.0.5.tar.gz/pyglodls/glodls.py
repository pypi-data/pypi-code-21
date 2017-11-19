#!/usr/bin/python

from __future__ import unicode_literals
import sys
import requests
from bs4 import BeautifulSoup
import re
import logging

log = logging.getLogger(__name__)

try:
    # Python 3 and later
    from urllib.parse import quote_plus
except ImportError:
    # Python 2
    from urllib import quote_plus


class BASE(object):
    URL = 'http://glodls.to'
    SEARCH = '/search_results.php?search={}'
    CATEGORY = '&cat={}'
    STATUS = '&includedead={}'
    SOURCE = '&inclexternal{}'
    LANGUAGE = '&lang={}'
    SORT = '&sort={}'
    ORDER = '&order={}'


class SORT(object):
    ADDED = 'id'
    NAME = 'name'
    COMMENTS = 'comments'
    SIZE = 'size'
    COMPLETED = 'times_completed'
    SEEDERS = 'seeders'
    LEECHERS = 'leechers'


class ORDER(object):
    ASCENDING = 'asc'
    DESCENDING = 'desc'


class CATEGORY(object):
    ALL = '0'
    MOVIES = '1'
    GAMES = '10'
    APPS = '18'
    MUSIC = '22'
    ANIME = '28'
    OTHER = '33'
    TV = '41'
    XXX = '50'
    BOOKS = '51'
    MOBILE = '52'
    PICTURES = '70'
    VIDEOS = '71'
    PACKS = '72'
    TUTORIALS = '74'
    FLAC = '75'


class STATUS(object):
    ACTIVE_TRANSFERS = '0'
    INCLUDE_DEAD = '1'
    ONLY_DEAD = '2'


class SOURCE(object):
    LOCAL_PLUS_EXTERNAL = '0'
    LOCAL_ONLY = '1'
    EXTERNAL_ONLY = '2'


class LANGUAGE(object):
    ALL = '0'
    ENGLISH = '1'
    FRENCH = '2'
    GERMAN = '3'
    ITALIAN = '4'
    JAPANESE = '5'
    SPANISH = '6'
    RUSSIAN = '7'
    CHINESE = '8'
    HINDI = '9'
    URDU = '10'
    ARABIC = '11'
    ROMANIAN = '17'
    DANISH = '20'
    NON_HINDI = '21'
    PORTUGUESE = '22'


class Torrent(object):
    def __init__(self, title, size, seeders, leechers, magnet):
        self.title = title
        self.size = size
        self.seeders = seeders
        self.leechers = leechers
        self.magnet = magnet

    @property
    def seeds(self):
        log.warning('Torrent.seeds is being deprecated and replaced by Torrent.seeders '
                    'for consistency in naming, please update your code.')
        return self.seeders

    def __repr__(self):
        return _valid_encoding('<Torrent(title={title})>'.format(title=self.title))

    def __str__(self):
        return _valid_encoding(self.title)

    def __unicode__(self):
        return self.title

    def __bool__(self):
        return bool(self.title)

    def __nonzero__(self):
        return bool(self.title)


def _valid_encoding(text):
    if not text:
        return
    if sys.version_info > (3,):
        return text
    else:
        return unicode(text).encode('utf-8')


# Convert gb to mb and make into float
def _gb_to_mb(size_data):
    size = size_data.replace(',', '')
    if size[-2:].lower() == 'gb':
        return float(size[:-3]) * 1024.0
    elif size[-2:].lower() == 'mb':
        return float(size[:-3])


def _parse_torrents(soup):
    torrents = []

    rows = soup.find_all('tr', {'class': 't-row'})
    for row in rows:
        try:
            tds = row.find_all('td')

            title = tds[1].find(title=True)['title']
            magnet = tds[3].a['href']
            size = _gb_to_mb(tds[4].text)
            seeders = int(re.sub(',', '', tds[5].text))
            leechers = int(re.sub(',', '', tds[6].text))

            torrents.append(Torrent(title, size, seeders, leechers, magnet))
        except TypeError as e:
            continue

    return torrents


def search(query, category=CATEGORY.ALL, status=STATUS.ACTIVE_TRANSFERS,
           source=SOURCE.LOCAL_PLUS_EXTERNAL, language=LANGUAGE.ALL, sort=SORT.ADDED,
           order=ORDER.DESCENDING):
    '''
    Search glodls.to

    Args:
        query (str)              -- Search term(s)
        category (Optional) -- CATEGORY.ALL | CATEGORY.TV | etc. (see class CATEGORY for full list)
        status (Optional)   -- STATUS.ACTIVE_TRANSFERS | STATUS.INCLUDE_DEAD | STATUS.ONLY_DEAD
        source (Optional)   -- SOURCE.LOCAL_PLUS_EXTERNAL | SOURCE.LOCAL_ONLY | SOURCE.EXTERNAL_ONLY
        language (Optional) -- LANGUAGE.ALL | LANGUAGE.ENGLISH | etc. (see class LANGUAGE for full list)
        sort (Optional)     -- SORT.ADDED | SORT.NAME | SORT.SEEDERS | etc. (see class SORT for full list)
        order (Optional)    -- ORDER.ASCENDING | ORDER.DESCENDING

    Returns:
        (list) pyglodls.Torrent objects
    '''
    headers = {'User-Agent' : "Magic Browser"}
    req_url = (BASE.URL + BASE.SEARCH.format(quote_plus(query)) +
               BASE.CATEGORY.format(category) + BASE.STATUS.format(status) +
               BASE.SOURCE.format(source) + BASE.LANGUAGE.format(language) +
               BASE.SORT.format(sort) + BASE.ORDER.format(order)
              )
    s = requests.get(req_url, headers=headers, verify=False)
    html = s.content
    soup = BeautifulSoup(html, 'html.parser')
    return _parse_torrents(soup)
