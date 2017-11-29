from __future__ import absolute_import, print_function, unicode_literals

import base64
import logging
import os
import sys
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
    # Python 3+
    from urllib.parse import urlparse

import paramiko
import pysftp
# paramiko.util.log_to_file(os.path.expanduser('~/paramiko.log'))

from manifest import config, utils

LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


class SFTPDownloader(object):
    """Downloads a file from SFTP."""

    def __init__(self):
        LOGGER.debug('Init SFTPDownloader')
        self.config = dict(config.items('sftp'))
        try:
            self.sftp = pysftp.Connection(
                host=self.config['server'],
                username=self.config['username'],
                password=base64.b64decode(self.config['password']))
        except paramiko.ssh_exception.AuthenticationException as e:
            LOGGER.error('SSH auth error: %s', e)
            utils.revert_manifest()
            utils.post_download()
            sys.exit(1)
        except paramiko.ssh_exception.SSHException as e:
            LOGGER.error('SSH error: %s', e)
            utils.revert_manifest()
            utils.post_download()
            sys.exit(1)

    def get_remote_file_path(self, filepath):
        """Return the actual remote file path."""
        # Parse URL
        url_parts = urlparse(filepath)
        # netloc = url_parts.netloc
        path = url_parts.path.lstrip('/')

        # If it is a absolute or relative url doesn't matter, we need to
        # create the remote file path
        filepath = self.config['remote_dir'].rstrip('/') + '/' + path
        remote_file = unquote(filepath)
        return remote_file

    def _download(self, remote_file, local_file):
        """Download helper to return True or False."""
        # LOGGER.debug('SFTP: %s ==> %s', remote_file, local_file)
        try:
            self.sftp.get(remote_file, local_file, preserve_mtime=True)
            return True
        except IOError as e:
            LOGGER.error('%s@%s:%s does not exist. Status code=%s',
                         self.config['username'], self.config['server'],
                         remote_file, str(e))
            return False

    def download_file(self, remote_file, local_file):
        """Downloads a file over SFTP and saves it to disk."""
        # Check if file exists locally, if not: download it
        if not os.path.exists(local_file):
            return self._download(remote_file, local_file)

        # File exists, if newer on remote: download it
        remote_file_mtime = self.sftp.stat(remote_file).st_mtime
        local_file_mtime = os.stat(local_file).st_mtime
        if remote_file_mtime != local_file_mtime:
            return self._download(remote_file, local_file)

    def close(self):
        """Close SFTP connection."""
        # Close SFTP connection
        self.sftp.close()
