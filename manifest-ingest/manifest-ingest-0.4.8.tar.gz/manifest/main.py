from __future__ import absolute_import, print_function, unicode_literals

import datetime
import logging
import multiprocessing
import os
import re
import sys
import time
try:
    # Python 2
    from urlparse import urlparse
except ImportError:
    # Python 3
    from urllib.parse import urlparse

from . import config, utils, args
from .httpdownloader import HTTPDownloader
from .s3downloader import S3Downloader
from .sftpdownloader import SFTPDownloader

LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------

sftp = None
s3 = None
pool = None


def download_file_s3(files):
    """Helper to allow multiprocessing."""
    remote_file, local_file = files
    try:
        s3.download_file(remote_file, local_file)
    except KeyboardInterrupt:
        pool.terminate()


def download_file_sftp(files):
    """Helper to allow multiprocessing."""
    remote_file, local_file = files
    try:
        sftp.download_file(remote_file, local_file)
    except KeyboardInterrupt:
        pool.terminate()


def download_file_http(files):
    """Helper to allow multiprocessing."""
    remote_file, local_file = files
    try:
        HTTPDownloader.download_file(remote_file, local_file)
    except KeyboardInterrupt:
        pool.terminate()


def run():
    """Run script."""
    global s3, sftp, pool
    start_time = time.time()
    LOGGER.debug('-' * 10)

    # Init downloaders that may be needed
    if config.has_section('sftp'):
        sftp = SFTPDownloader()

    if config.has_section('s3'):
        s3 = S3Downloader()

    # Make local_dir
    local_dir = os.path.expanduser(config.get('default', 'local_dir'))
    utils.make_dir(local_dir)

    # Backup existing manifest
    utils.backup_manifest()

    # Get manifest from API endpoint
    parsed_json = utils.get_manifest()
    # print(parsed_json)

    if not parsed_json:
        LOGGER.warning('Empty manifest. Aborting...')
        sys.exit()

    # Save manifest
    utils.save_manifest(parsed_json)

    # Find all the keys that match the key we're looking for
    keys = config.get('default', 'keys')
    file_list = utils.find_all_keys(parsed_json, keys)
    # total_files = len(file_list)

    # Download files
    LOGGER.debug('Downloading manifest files...')

    # Used for pool only, backwards compat if not set in config
    concurrent_downloads = 1
    if config.has_option('default', 'concurrent_downloads'):
        concurrent_downloads = config.getint('default', 'concurrent_downloads')
    #     if config.has_section('sftp') and concurrent_downloads > 1:
    #         raise ValueError('SFTP currently does not work with concurrent downloads, please set concurrent_downloads=1')
    # LOGGER.debug('Concurrent downloads: %s', concurrent_downloads)

    s3_args = []
    http_args = []

    file_list.sort()

    # Download files
    for filepath in file_list:
        # Parse URL to get info we need to create local file structure
        url_parts = urlparse(filepath)
        # netloc = re.sub(r':\d+', '', url_parts.netloc)  # strip port if any
        netloc = url_parts.netloc.replace(':', '_')
        path = url_parts.path.lstrip('/')

        # Ensure the local dir structure matches our remote dir structure
        local_file = os.path.join(local_dir, netloc, path)
        utils.make_dir(os.path.dirname(local_file))

        # Handle Amazon S3 URLS
        if 's3.amazonaws.com' in netloc:
            if config.has_section('s3') and s3.bucket_name in path:
                remote_file = s3.get_remote_file_path(path)
                s3_args.append((remote_file, local_file))
            else:
                remote_file = HTTPDownloader.get_remote_file_path(filepath)
                http_args.append((remote_file, local_file))

        # Handle other urls via SFTP or HTTP
        else:
            if config.has_section('sftp'):
                remote_file = sftp.get_remote_file_path(filepath)
                sftp_args.append((remote_file, local_file))
                # SFTP does not support concurrency so we just download
                sftp.download_file(remote_file, local_file)
            else:
                remote_file = HTTPDownloader.get_remote_file_path(filepath)
                http_args.append((remote_file, local_file))

    # Process the downloads
    if concurrent_downloads >= 1:
        LOGGER.debug('Use multiprocessing...')
        LOGGER.debug('Concurrent downloads: %s', concurrent_downloads)
        pool = multiprocessing.Pool(processes=concurrent_downloads)
        pool.map(download_file_s3, s3_args)
        pool.map(download_file_http, http_args)
        pool.close()
        pool.join()

    # Cleanup
    if config.has_section('sftp'):
        sftp.close()

    end_time = time.time()

    elapsed = str(datetime.timedelta(seconds=(end_time - start_time)))
    LOGGER.debug('Time Elapsed: %s', elapsed)

    # Run a command post download
    utils.post_download()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    run()
