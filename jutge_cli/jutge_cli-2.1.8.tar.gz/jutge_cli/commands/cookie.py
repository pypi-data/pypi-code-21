#!/usr/bin/python3

# Copyright (C) 2017  Aleix Boné (abone9999 at gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Save and read cookie from args or /tmp file
"""

from importlib.util import find_spec
from logging import getLogger
from os import remove
from os.path import isfile
from tempfile import gettempdir

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import ConnectionError

PARSER = 'lxml' if find_spec('lxml') is not None else 'html.parser'

LOG = getLogger('jutge.cookie')


def get_cookie(cookie: str, no_download: 'Boolean',
        skip_check: 'Boolean' = False, **kwargs) -> dict:
    """Wrapper around Cookie class that returns cookie dict

    :param cookie: cookie value
    :param no_download: do not download from jutge.org
    :param skip_check: skip cookie check

    :return: cookie dict with cookie as PHPSESSID (empty if cookie not valid)
    """

    cookie_container = Cookie(cookie, no_download, skip_check, **kwargs)
    if cookie_container.cookie is None or\
            (not skip_check and cookie_container.check_cookie() is None):
        return {}
    return dict(PHPSESSID=cookie_container.cookie)


class Cookie:

    """Provides methods to save and read cookie from file or arguments
    """

    def __init__(self, cookie: str = None, no_download: 'Boolean' = False,
            skip_check: 'Boolean' = False, subcmd: str = 'cookie', **kwargs):
        """Save args and initialize class variables

        :param cookie: cookie value
        :param no_download: do not download from jutge.org
        :param skip_check: skip cookie check
        """

        self.file_name = '{}/jutge_cli_cookie'.format(gettempdir())
        self.has_cookie = False
        self.check_done = False
        self.username = None
        self.cookie = None

        self.no_download = no_download

        if cookie == 'delete':
            remove(self.file_name)
            return

        if cookie not in (None, 'show', 'print'):
            self.cookie = cookie
            self.has_cookie = True
            if not skip_check:
                if self.check_cookie() is None:
                    LOG.error('Invalid cookie (if you want to \
skip the check use --skip-check)')

                    exit(3)
            self.make_file()
        else:
            if isfile(self.file_name):
                with open(self.file_name) as cookie_file:
                    self.cookie = cookie_file.readline().strip()
                    self.has_cookie = True
                LOG.debug(self.cookie)

            if subcmd == 'cookie':
                print(self.cookie)
            elif not self.has_cookie:
                LOG.warning('No cookie saved')

    def make_file(self):
        """Save cookie to file: /tmp/jutge_cookie (or equivalent)
        """
        LOG.debug('writing file ' + self.file_name)
        with open(self.file_name, 'w') as cookie_file:
            cookie_file.write(self.cookie + '\n')

    def check_cookie(self) -> str:
        """Check that cookie is valid by downloading dashboard

        :return: username if cookie succesfull or None on failure
        """
        if self.check_done:
            return self.username

        if self.no_download:
            LOG.debug('Cannot check cookie if no-download active')
            return None

        cookies = {'PHPSESSID' : self.cookie}
        web = 'https://jutge.org/dashboard'

        try:
            response = get(web, cookies=cookies)
        except ConnectionError:
            LOG.error('Connection Error, are you connected to the internet?')
            exit(1)
        soup = BeautifulSoup(response.text, PARSER)

        try:
            tags = soup.findAll('a', {'href' : '/profile'})
            for tag in tags:
                LOG.debug(tag.b)
                if tag.b is not None:
                    self.username = tag.b.contents[0]
                    LOG.debug(tag.b)
                    break

            LOG.debug('Logged in as: %s', self.username)

        except AttributeError:
            LOG.debug('Invalid cookie: %s', self.cookie)
            self.username = None

        self.check_done = True
        return self.username
