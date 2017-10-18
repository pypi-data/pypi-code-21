# coding=utf-8
# Author: Bart Sommer <bart.sommer88@gmail.com>
#
# URL: https://sickrage.ca
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, unicode_literals

import re

from requests.utils import dict_from_cookiejar

import sickrage
from sickrage.core.caches.tv_cache import TVCache
from sickrage.core.exceptions import AuthException
from sickrage.core.helpers import bs4_parser, try_int, convert_size
from sickrage.providers import TorrentProvider


class ImmortalseedProvider(TorrentProvider):
    def __init__(self):
        super(ImmortalseedProvider, self).__init__('Immortalseed', 'https://immortalseed.me', True)

        # Credentials
        self.username = None
        self.password = None
        self.passkey = None

        # Torrent Stats
        self.minseed = None
        self.minleech = None
        self.freeleech = None

        # URLs
        self.urls.update({
            'login': '{base_url}/takelogin.php'.format(**self.urls),
            'search': '{base_url}/browse.php'.format(**self.urls),
            'rss': '{base_url}/rss.php'.format(**self.urls),
        })

        # Proper Strings
        self.proper_strings = ['PROPER', 'REPACK']

        # Cache
        self.cache = ImmortalseedCache(self, min_time=20)

    def _check_auth(self):

        if not self.username or not self.password:
            raise AuthException("Your authentication credentials for " + self.name + " are missing, check your config.")

        return True

    def _check_auth_from_data(self, data):
        if not self.passkey:
            sickrage.srCore.srLogger.warning('Invalid passkey. Check your settings')

        return True

    def login(self):
        if any(dict_from_cookiejar(sickrage.srCore.srWebSession.cookies).values()):
            return True

        login_params = {
            'username': self.username,
            'password': self.password,
        }

        response = sickrage.srCore.srWebSession.post(self.urls['login'], data=login_params).text
        if not response:
            sickrage.srCore.srLogger.warning("Unable to connect to provider")
            return False

        if re.search('Username or password incorrect!', response):
            sickrage.srCore.srLogger.warning("Invalid username or password. Check your settings")
            return False

        return True

    def search(self, search_strings, age=0, ep_obj=None):
        results = []
        if not self.login():
            return results

        # Search Params
        search_params = {
            'do': 'search',
            'include_dead_torrents': 'no',
            'search_type': 't_name',
            'category': 0,
            'keywords': ''
        }

        def process_column_header(td):
            td_title = ''
            if td.img:
                td_title = td.img.get('title', td.get_text(strip=True))
            if not td_title:
                td_title = td.get_text(strip=True)
            return td_title

        for mode in search_strings:

            sickrage.srCore.srLogger.debug("Search Mode: {0}".format(mode))

            for search_string in search_strings[mode]:
                if mode != 'RSS':
                    sickrage.srCore.srLogger.debug("Search string: {0}".format(search_string))
                    search_params['keywords'] = search_string

                data = sickrage.srCore.srWebSession.get(self.urls['search'], params=search_params).text
                if not data:
                    sickrage.srCore.srLogger.debug("No data returned from provider")
                    continue

                with bs4_parser(data) as html:
                    torrent_table = html.find('table', id='sortabletable')
                    torrent_rows = torrent_table('tr') if torrent_table else []

                    # Continue only if at least one Release is found
                    if len(torrent_rows) < 2:
                        sickrage.srCore.srLogger.debug("Data returned from provider does not contain any torrents")
                        continue

                    labels = [process_column_header(label) for label in torrent_rows[0]('td')]

                    # Skip column headers
                    for result in torrent_rows[1:]:
                        try:
                            title = result.find('div', class_='tooltip-target').get_text(strip=True)
                            # skip if torrent has been nuked due to poor quality
                            if title.startswith('Nuked.'):
                                continue
                            download_url = result.find(
                                'img', title='Click to Download this Torrent in SSL!').parent['href']
                            if not all([title, download_url]):
                                continue

                            cells = result('td')
                            seeders = try_int(cells[labels.index('Seeders')].get_text(strip=True))
                            leechers = try_int(cells[labels.index('Leechers')].get_text(strip=True))

                            # Filter unseeded torrent
                            if seeders < self.minseed or leechers < self.minleech:
                                if mode != 'RSS':
                                    sickrage.srCore.srLogger.debug("Discarding torrent because it doesn't meet the"
                                                                   " minimum seeders or leechers: {0} (S:{1} L:{2})".format
                                                                   (title, seeders, leechers))
                                continue

                            torrent_size = cells[labels.index('Size')].get_text(strip=True)
                            size = convert_size(torrent_size, -1)

                            item = {'title': title, 'link': download_url, 'size': size, 'seeders': seeders,
                                    'leechers': leechers, 'hash': ''}

                            if mode != 'RSS':
                                sickrage.srCore.srLogger.debug("Found result: {}".format(title))

                            results.append(item)
                        except StandardError:
                            continue

        # Sort all the items by seeders if available
        results.sort(key=lambda k: try_int(k.get('seeders', 0)), reverse=True)

        return results


class ImmortalseedCache(TVCache):
    def _get_rss_data(self):
        params = {
            'secret_key': self.provider.passkey,
            'feedtype': 'downloadssl',
            'timezone': '-5',
            'categories': '44,32,7,47,8,48,9',
            'showrows': '50',
        }

        return self.getRSSFeed(self.provider.urls['rss'], params=params)

    def _check_auth(self, data):
        return self.provider._check_auth_from_data(data)