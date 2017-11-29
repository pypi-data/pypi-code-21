from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import re
import shutil
try:
    # Python 2
    from urllib import unquote
except ImportError:
    # Python 3+
    from urllib.parse import unquote

try:
    # Python 2
    from urlparse import urlparse
except ImportError:
    # Python 3
    from urllib.parse import urlparse

import requests

from manifest import config

LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


class HTTPDownloader(object):
    """
    Download a file over HTTP.
    May be overkill for our needs, but keeps the API consistent among
    S3, SFTP and HTTP.
    """

    # def __init__(self):
    #      LOGGER.debug('Init HTTPDownloader')

    @staticmethod
    def get_remote_file_path(filepath):
        """Returns the full remote path."""
        # Parse URL
        url_parts = urlparse(filepath)
        netloc = url_parts.netloc
        path = url_parts.path.lstrip('/')

        # If relative path, then prepend the base_url
        if not netloc:
            base_url = config.get('default', 'base_url').rstrip('/')
            filepath = base_url + '/' + path
        remote_file = unquote(filepath)
        return remote_file

    @staticmethod
    def download_file(remote_file, local_file):
        """Downloads a file over HTTP and saves it to disk."""
        # Check if file exists locally, if not: download it
        if not os.path.exists(local_file):
            # LOGGER.debug('HTTP: %s ==> %s', remote_file, local_file)
            try:
                r = requests.get(remote_file, stream=True)
            except requests.exceptions.ConnectionError as e:
                LOGGER.error(str(e))
                return False
            except requests.exceptions.Timeout as e:
                LOGGER.error(str(e))
                return False

            if r.status_code != 200:
                LOGGER.error('%s does not exist. Status code=%s',
                             remote_file, r.status_code)
                return False

            with open(local_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            return True

        return False
