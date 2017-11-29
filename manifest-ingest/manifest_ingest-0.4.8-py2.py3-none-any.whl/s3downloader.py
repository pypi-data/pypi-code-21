from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import re

import boto3
import botocore

from . import config
from .utils import md5_hash

LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


class S3Downloader(object):
    """Downloads a file from Amazon S3."""

    def __init__(self):
        LOGGER.debug('Init S3Downloader')
        # Access key and secret are now located in ~/.aws/credentials
        session = boto3.Session(profile_name=config.get('s3', 'profile_name'))
        self.s3_client = session.client('s3')
        s3_resource = session.resource('s3')

        self.bucket_name = config.get('s3', 'bucket_name')
        self.bucket = s3_resource.Bucket(self.bucket_name)

    def md5_sum(self, resource_name):
        """
        Return a md5 hash of a file.

        Note that the ETag is not always the md5 hash of a file if a
        multi-part upload. At worst, this just means we'll end up
        downloading it again.
        """
        try:
            md5sum = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=resource_name
            )['ETag'][1:-1]
        except botocore.exceptions.ClientError:
            md5sum = None
        return md5sum

    def get_remote_file_path(self, filepath):
        """Returns the S3 key from the filepath."""
        s3_key = re.sub(r'https?://(.+\.)?s3.amazonaws.com/', '', filepath)
        s3_key = filepath.replace(self.bucket_name + '/', '')
        return s3_key

    def _download(self, remote_file, local_file):
        """Download helper to return True or False."""
        # LOGGER.debug('S3: %s ==> %s', remote_file, local_file)
        try:
            self.bucket.download_file(remote_file, local_file)
            return True
        except botocore.exceptions.ClientError as e:
            LOGGER.error('%s does not exist. Status code=%s',
                         remote_file, e.response['Error']['Code'])
            return False

    def download_file(self, remote_file, local_file):
        """Download a file from S3 and saves it to disk."""
        # Check if file exists locally, if not: download it
        if not os.path.exists(local_file):
            return self._download(remote_file, local_file)

        # File exists, if newer on remote: download it
        if config.getboolean('s3', 'compare_md5'):
            md5 = md5_hash(local_file)
            etag = self.md5_sum(remote_file)
            if etag != md5:
                # LOGGER.debug('"%s" %s != %s' % (remote_file, etag, md5))
                return self._download(remote_file, local_file)
            return False
