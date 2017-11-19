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

"""Module to get code from filename of flags and expand it if needed

Main function is: get_code()
"""

from glob import glob
from importlib.util import find_spec
from logging import getLogger
from os.path import basename
from re import search

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import ConnectionError

PARSER = 'lxml' if find_spec('lxml') is not None else 'html.parser'

LOG = getLogger('jutge.get_code')


def __expand_subcode__(subcode: str, database: str, cookies: dict,
        no_download: 'Boolean', **kwargs) -> str:
    """Return code from subcode

    This function uses info from the database if available or connects
    to jutge.org to retrieve it

    Returns subcode with locale appended (_ca,_en,_es ...) or None on failure

    :param subcode: subcode
    :param database: database folder path
    :param cookie: dict cookies
    :param no_download: do not connect to jutge.org

    :return: code
    """

    problem_folder = glob('{}/{}_*'.format(database, subcode))

    if problem_folder:
        code = problem_folder[0].split('/')[-1]
    else:

        if no_download:
            LOG.error('Invalid code')
            return None

        url = 'https://jutge.org/problems/' + subcode

        try:
            response = get(url, cookies=cookies)
        except ConnectionError:
            LOG.error('Connection Error, are you connected to the internet?')
            exit(1)
        soup = BeautifulSoup(response.text, PARSER)

        try:
            code = soup.find('title').text.split('-')[1].strip()
        except KeyError:
            LOG.error('Invalid code')
            return None

        if code == 'Error':
            LOG.error('Invalid code')
            return None
        return code


def __match_regex__(regex: str, text: str) -> str:
    """Return regex match on text

    :param regex: regex to use
    :param text: text where regex should match

    :return: regex match or None if failed
    """

    LOG.debug('match regex %s, text %s', regex, text)

    try:
        temp = search('(' + regex + ')', text).group(1)
    except AttributeError:  # regex failed, return none
        return None
    LOG.debug(temp)
    return temp


def get_code(database: str, regex: str, no_download: 'Boolean', code: str = None,
        prog: str = None, **kwargs) -> str:
    """Return problem code

    :param database: database folder path
    :param regex: regex used to match code
    :param no_download: do not connect to jutge.org
    :param code: problem code
    :param prog: problem file

    :return: code
    """

    LOG.debug('prog %s, code %s', prog, code)

    if code is not None:

        if '_' not in code:
            code = __expand_subcode__(subcode=code, database=database,
                                      no_download=no_download, **kwargs)

        LOG.debug('code in args %s', code)

        return code

    if isinstance(prog, str):
        prog_name = basename(prog)
    else:
        try:
            prog_name = basename(prog.name)
        except AttributeError:
            prog_name = None

    if prog_name is None:
        LOG.warning('No code found')
        return None

    code = __match_regex__(regex=regex, text=prog_name)

    if code is None and '_' in regex:

        LOG.warning('Regex failed, trying to match subcode')

        regex_v2 = regex.split('_')[0]
        subcode = __match_regex__(regex=regex_v2, text=prog_name)
        if subcode is None:
            LOG.error('Cannot find code in filename')
            return None

        code = __expand_subcode__(subcode, database=database,
                                  no_download=no_download, **kwargs)

        if code is None:
            return subcode
    return code
