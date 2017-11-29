from __future__ import absolute_import, print_function, unicode_literals

import hashlib
import io
import json
import logging
import os
import re
import shlex
import shutil
import sys
import time
from pprint import pprint
from subprocess import PIPE, Popen

import requests

from manifest import config

try:
    # Python 2
    from urlparse import urlparse
except ImportError:
    # Python 3
    from urllib.parse import urlparse

# -----------------------------------------------------------------------------

LOGGER = logging.getLogger(__name__)
current_retries = 0


def make_dir(dirpath):
    """Lazy shortcut to make a dir if it does not exist."""
    try:
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
    except OSError as err:
        LOGGER.error(str(err))
        sys.exit(1)


def exec_cmd(cmd):
    """Run a command and return the status, standard output and error."""
    LOGGER.debug('Execute command: %s', cmd)
    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    # I like to get True or False rather than 0 (True) or 1 (False)
    # which is just backwards as usually 0 is False and 1 is True
    status = not bool(proc.returncode)
    return (status, stdout, stderr)


def post_download():
    """Post download action. Run a command."""
    if not config.has_section('post_download'):
        return

    post_cfg = dict(config.items('post_download'))

    try:
        exec_cmd(post_cfg['command'])
    except OSError as err:
        LOGGER.error('OS error: %s', err)

    LOGGER.debug('Exiting...')
    sys.exit()


# def find_all_keys(obj, keys):
#     """Find all keys in parsed json. (http://bit.ly/1RnjFaa)"""
#     keys = re.compile(keys)

#     results = set()
#     keys_found = set()

#     def _find_all(obj, key):
#         """Internal method we call recursively."""
#         if isinstance(obj, dict):
#             for item in obj:
#                 if isinstance(obj[item], (list, dict)):
#                     _find_all(obj[item], key)
#                 elif re.match(key, item):
#                     # print(item, obj[item])
#                     results.add(obj[item])
#                     # Keep track of keys we found for logging purposes
#                     keys_found.add(item)
#         elif isinstance(obj, list):
#             for item in obj:
#                 if isinstance(item, (list, dict)):
#                     _find_all(item, key)

#     _find_all(obj, keys)

#     # Remove None values we may get for keys that are not found
#     results = [x for x in results if x is not None and x is not '']

#     keys_found = ', '.join(keys_found)
#     LOGGER.debug('Found %s unique files matching keys: %s',
#                  len(results), keys_found)

#     return results


def find_all_keys(obj, keys):
    """Find all target keys with URLs in parsed json."""
    data = json.dumps(obj, indent=4)
    regex = r'"' + keys + '": "((https?://|/).+)"'
    results = set()
    for match in re.finditer(regex, data):
        results.add(match.group(2))
    results = [x for x in results if x is not None and x is not '']
    LOGGER.debug('Found %s unique files matching regex: %s',
                 len(results), regex)
    return results


def get_manifest():
    """Returns manifest as JSON."""
    global current_retries

    token = None
    if config.has_option('default', 'api_token'):
        token = config.get('default', 'api_token')
    url = config.get('default', 'api_url')

    LOGGER.debug('Getting manifest: %s', url)
    payload = {'format': 'json'}
    headers = {}

    # Make the API request and return the response or exit if exception thrown
    if token:
        headers = {'authorization': '{}'.format(token)}
    try:
        response = requests.get(url, params=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    except (requests.ConnectionError) as err:
        LOGGER.error('Connection error: %s', err)
        if current_retries < config.getint('default', 'max_retries'):
            LOGGER.debug('Retrying in 5 seconds...')
            current_retries += 1
            time.sleep(5)
            return get_manifest()
        else:
            LOGGER.debug('Max retries reached. Moving on...')
            post_download()
            sys.exit(1)

    except (requests.HTTPError) as err:
        LOGGER.error('HTTP error: %s', err)
        post_download()
        sys.exit(1)


def get_manifest_filename():
    """Get the manifest filename safely for backwards compat.
    e.g. - `manifest_filename` is missing from the config file."""
    if config.has_option('default', 'manifest_filename'):
        return config.get('default', 'manifest_filename')
    return 'manifest.json'


def backup_manifest():
    """Backup current manifest."""
    local_dir = os.path.expanduser(config.get('default', 'local_dir'))
    filepath = os.path.join(local_dir, get_manifest_filename())
    filepath_bak = filepath + '.bak'
    if os.path.exists(filepath):
        # LOGGER.debug('Backing up current manifest...')
        shutil.copyfile(filepath, filepath_bak)
        # LOGGER.debug(filepath_bak)


def save_manifest(json_content):
    """Saves manifest and does a regex replace to create relative URLs."""
    local_dir = os.path.expanduser(config.get('default', 'local_dir'))
    filepath = os.path.join(local_dir, get_manifest_filename())
    LOGGER.debug('Saving manifest to "%s"', filepath)

    # Save it human readable
    with io.open(filepath, 'w', encoding='utf-8') as f:
        data = json.dumps(json_content, sort_keys=True, indent=4)

        # Strip stuff from the URLs
        regex = r': "(https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,4})'
        data = re.sub(regex, ": \"\\1_\\2", data)

        regex = r': "(https?://|/)'
        data = re.sub(regex, ': "', data)
        try:
            f.write(unicode(data))
        except:
            f.write(data)


def revert_manifest():
    """Revert to original manifest."""
    local_dir = os.path.expanduser(config.get('default', 'local_dir'))
    filepath_bak = os.path.join(local_dir, get_manifest_filename() + '.bak')
    filepath = os.path.join(local_dir, get_manifest_filename())
    if os.path.exists(filepath_bak):
        LOGGER.debug('Reverting to original manifest...')
        os.remove(filepath)
        shutil.copyfile(filepath_bak, filepath)
        os.remove(filepath_bak)


def md5_hash(filepath):
    """Return a md5 hash of a file."""
    md5sum = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5sum.update(chunk)
    return md5sum.hexdigest()
