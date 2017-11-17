from __future__ import unicode_literals

import logging
from google.appengine.api import urlfetch
from requests_toolbelt.adapters import appengine

from . import get as base_get
from . import put as base_put
from . import post as base_post


logger = logging.getLogger(__name__)

appengine.monkeypatch()


def get(url, headers, key_location, fetch_deadline=15):
    urlfetch.set_default_fetch_deadline(fetch_deadline)

    return base_get(url=url, headers=headers, key_location=key_location)


def put(url, headers, key_location, data, fetch_deadline=15):
    urlfetch.set_default_fetch_deadline(fetch_deadline)

    return base_put(url=url, headers=headers, key_location=key_location, data=data)


def post(url, headers, key_location, data, fetch_deadline=15):
    urlfetch.set_default_fetch_deadline(fetch_deadline)

    return base_post(url=url, headers=headers, key_location=key_location, data=data)
