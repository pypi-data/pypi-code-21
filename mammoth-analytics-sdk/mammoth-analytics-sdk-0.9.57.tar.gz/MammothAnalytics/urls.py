from __future__ import unicode_literals
import logging
from urlparse import urljoin
import const

log = logging.getLogger(__name__)



def get_url(subpath):
    return const.API + subpath

