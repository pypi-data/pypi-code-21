#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re
import logging

log = logging.getLogger(__name__)


class BASE(object):
    url = 'http://1337x.to'
    search = '/search/{}/1/'


class Torrent(object):
    def __init__(self, title, magnet, size, seeders, leeches):
        self.title = title
        self.magnet = magnet
        self.size = size
        self.seeders = seeders
        self.leeches = leeches

    @property
    def seeds(self):
        log.warning('Torrent.seeds is being deprecated and replaced by Torrent.seeders '
                    'for consistency in naming, please update your code.')
        return self.seeders


# Convert gb to mb and make into float
def _gb_to_mb(size_data):
    size = size_data.replace(',', '')
    if size[-2:].lower() == 'gb':
        return float(size[:-3]) * 1024.0
    elif size[-2:].lower() == 'mb':
        return float(size[:-3])


def search(query):
    headers = {'User-Agent' : "Magic Browser"}
    req_url = BASE.url + BASE.search.format(quote_plus(query))
    s = requests.get(req_url, headers=headers, verify=False)
    html = s.content
    soup = BeautifulSoup(html, 'html.parser')
    tbody = soup.find('tbody')
    try:
        trs = tbody.find_all('tr')
    except AttributeError as e:
        return []

    torrents = []
    for tr in trs:
        link = tr.find_all('a')[1]['href']
        tds = tr.find_all('td')
        title = tds[0].text
        size_raw = tds[4].text
        m = re.search('[mM][bB]|[gG][bB]', size_raw)
        if m:
            size_split = size_raw.split(m.group())[0] + m.group()
            size = _gb_to_mb(size_split)
        else:
            size = 0
        seeders = int(re.sub(',', '', tds[1].text))
        leeches = int(re.sub(',', '', tds[2].text))

        req_url = BASE.url + link
        s = requests.get(req_url, headers=headers, verify=False)
        html = s.content
        soup = BeautifulSoup(html, 'html.parser')
        down_ul = soup.find('ul', {'class': 'download-links-dontblock btn-wrap-list'})
        mag = down_ul.li.a.get('href')

        torrents.append(Torrent(title, mag, size, seeders, leeches))

    return torrents
