# Copyright (C) 2016 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

# these are all kinda inappropriate for pytest patterns
# pylint: disable=old-style-class, no-init, protected-access, no-self-use, unused-argument

"""Test configuration and fixtures."""

from __future__ import unicode_literals
from __future__ import print_function

import json
import os
import re
import shutil
import subprocess
import time

import mock
import pytest

import fedfind.const
import fedfind.helpers

# Fake data for the collections fixture
COLLECTIONS_JSON = [
    {
        "allow_retire": True,
        "branchname": "master",
        "date_created": "2014-05-14 12:36:15",
        "date_updated": "2016-02-23 22:56:34",
        "dist_tag": ".fc25",
        "koji_name": "rawhide",
        "name": "Fedora",
        "status": "Under Development",
        "version": "devel"
    },
    {
        "allow_retire": False,
        "branchname": "f22",
        "date_created": "2015-02-10 14:00:01",
        "date_updated": "2015-02-10 14:00:01",
        "dist_tag": ".fc22",
        "koji_name": "f22",
        "name": "Fedora",
        "status": "Active",
        "version": "22"
    },
    {
        "allow_retire": False,
        "branchname": "f23",
        "date_created": "2015-07-14 18:13:12",
        "date_updated": "2015-07-14 18:13:12",
        "dist_tag": ".fc23",
        "koji_name": "f23",
        "name": "Fedora",
        "status": "Active",
        "version": "23"
    },
    {
        "allow_retire": True,
        "branchname": "f24",
        "date_created": "2016-02-23 22:57:55",
        "date_updated": "2016-02-25 20:39:53",
        "dist_tag": ".fc24",
        "koji_name": "f24",
        "name": "Fedora",
        "status": "Under Development",
        "version": "24"
    }
]

@pytest.fixture(scope="session")
def http(request):
    """Run a SimpleHTTPServer that we can use as a fake dl.fp.o. Serve
    the contents of tests/data/http, for the entire test session. We
    just do this with subprocess as we need it to run parallel to the
    tests and this is really the easiest way.
    """
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'data', 'http')
    # Always use python2 for this (for now)
    args = ("python2", "-m", "SimpleHTTPServer", "5001")
    proc = subprocess.Popen(args, cwd=root)
    # this is rather ugly, but if we yield immediately, the tests will
    # try to use the server before it's actually started up. I don't
    # know of a way to wait for the sub-process to print a specific
    # message but *not* wait for it to complete (communicate() waits
    # for completion), so just wait a second.
    time.sleep(1)
    # Redefine the HTTPS_DL constant to point to the fake server
    fedfind.const.HTTPS_DL = 'http://localhost:5001/pub'

    def fin():
        """Teardown: kill the server. We don't use the 'yield fixture'
        feature here because we want these tests to run on EL 6, and
        the steam-powered ancient pytest in EL 6 doesn't have it.
        """
        proc.kill()
    request.addfinalizer(fin)

    return None

@pytest.fixture(scope="function")
def clean_home(request):
    """Provides a fake user home directory, at data/home/ under the
    tests directory. Before the test, re-create it, change the cache
    dir global to use it, and patch os.path.expanduser to return it.
    After the test, delete it and clean up the other bits. Yields
    the full path.
    """
    home = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'home')
    if os.path.exists(home):
        shutil.rmtree(home)
    cachedir = os.path.join(home, '.cache', 'fedfind')
    os.makedirs(cachedir)
    patcher = mock.patch('os.path.expanduser', return_value=home, autospec=True)
    patcher.start()
    origcache = fedfind.helpers.CACHEDIR
    fedfind.helpers.CACHEDIR = cachedir

    def fin():
        """Teardown: stop the patcher and wipe the directory. As per
        http, we can't use the yield syntax here because EL 6.
        """
        patcher.stop()
        fedfind.helpers.CACHEDIR = origcache
        if os.path.exists(home):
            shutil.rmtree(home)
    request.addfinalizer(fin)

    return home

def fake_pdc_query(path, params=None):
    """A fake pdc_query that doesn't really hit PDC, it just returns
    canned information (some inline, some loaded from tests/data) for
    queries the tests are known to make.
    """
    # match how pdc_query sanitizes the path
    path = path.strip('/') + '/'
    # composes query. This is hit for cid_from_label.
    if path == 'composes/':
        # Knowns in (release, label, composeid) form:
        composes = (
            ('fedora-24', 'RC-1.2', 'Fedora-24-20160614.0'),
            ('fedora-25', 'RC-1.3', 'Fedora-25-20161115.0'),
        )
        for (rel, label, cid) in composes:
            # We can make this matching smarter if needed, for now
            # it's specific to cid_from_label
            if params['release'] == rel and params['compose_label'] == label:
                return [{'compose_id': cid, 'release': rel, 'compose_label': label}]
        # fallthrough
        return []

    # compose-images query. Just grab the compose ID and look for a
    # backing file to return.
    compimgs = re.compile(r'compose-images/(.*)/')
    match = compimgs.match(path)
    if match:
        fname = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'data', 'pdc-compimages-{0}.json'.format(match.group(1)))
        with open(fname, 'r') as datafh:
            return json.loads(datafh.read())

@pytest.fixture(scope="function")
def pdc(request):
    """Mock fedfind.helpers.pdc_query with fake_pdc_query."""
    patcher = mock.patch('fedfind.helpers.pdc_query', fake_pdc_query)
    patcher.start()

    def fin():
        """Teardown: stop the patcher and wipe the directory. As per
        http, we can't use the yield syntax here because EL 6.
        """
        patcher.stop()
    request.addfinalizer(fin)

    return None

@pytest.fixture(scope="function")
def collections(request):
    """Mock fedfind.helpers._get_collections to return test data."""
    patcher = mock.patch('fedfind.helpers._get_collections', return_value=COLLECTIONS_JSON,
                         autospec=True)
    patcher.start()

    def fin():
        """Teardown: stop the patcher and wipe the directory. As per
        http, we can't use the yield syntax here because EL 6.
        """
        patcher.stop()
    request.addfinalizer(fin)

    return None

@pytest.fixture(scope="function")
def json_collections(request):
    """Mock fedfind.helpers.download_json to return collections test
    data (wrapped appropriately). Returns the mock so tests can check
    its call count, and the test data so they can verify it.
    """
    patcher = mock.patch(
        'fedfind.helpers.download_json', return_value={'collections': COLLECTIONS_JSON},
        autospec=True)
    mocked = patcher.start()

    def fin():
        """Teardown: stop the patcher and wipe the directory. As per
        http, we can't use the yield syntax here because EL 6.
        """
        patcher.stop()
    request.addfinalizer(fin)

    return (mocked, COLLECTIONS_JSON)

# vim: set textwidth=100 ts=8 et sw=4:
