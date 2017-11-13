from base64 import b64encode
from datetime import datetime
import functools
import logging
import time
import os
import shutil
import os.path as op

import httpsig.requests_auth
import requests
import pytz

from .conf import read_key
from .digest import make_digest, compare_digest, InvalidDigest
from .error import CommandError
from .tags import TagStore, TagError, HASH_REGEX, TAG_REGEX
from .utils import get_timezone

SERVER = 'https://api.pozetron.com'
USER_ROOT = '/user/v1/'
_PYTHON_EXTENSIONS = ('.py', '.mpy')

# Micropython implementations of time() use different epoch starts:
# 1970-01-01 on Unix
# 2000-01-01 on devices
# We use 2000-01-01 00:00:00 UTC for Timestamp header.
EPOCH = 946684800

# Max seconds between response Timestamp header and device's current time
MAX_TIMESTAMP_DELTA = 50


class HTTPSignatureAuth(httpsig.requests_auth.HTTPSignatureAuth):
    """Subclass HTTPSignatureAuth to add Digest header."""

    def __call__(self, r):
        if r.body is not None:
            r.headers['Digest'] = make_digest(r.body)
        return super(HTTPSignatureAuth, self).__call__(r)


class _Session(requests.Session):
    """This is for more compact code."""

    def __init__(self, key_id, secret):
        super(_Session, self).__init__()
        self.__key_id = key_id
        self.__secret = secret

    def get_absolute_url(self, url):
        return SERVER + USER_ROOT + url.lstrip('/')

    def __make_auth(self, method, **kwargs):
        """We make auth object on the fly, because Digest header is added for POST with body."""
        # List of headers in HTTP Signature depends on request type
        required_headers = ['(request-target)', 'host', 'timestamp']
        if kwargs.get('data') is not None or kwargs.get('json') is not None:
            required_headers.append('digest')
        # We re-create auth for EVERY request.
        # This may look unoptimized, but none of the commands use more than one request anyway.
        self.auth = HTTPSignatureAuth(key_id=self.__key_id, secret=self.__secret,
                                      algorithm='hmac-sha256',
                                      headers=required_headers)
        logging.getLogger('verbose').debug('Session key_id={!r}, headers={!r}'
                                           .format(self.__key_id, required_headers))

    def request(self, method, url, headers=None, allow_404=False, **kwargs):
        self.__make_auth(method, **kwargs)
        logger = logging.getLogger('verbose')
        logger.debug('{} {}'.format(method, url))
        url = self.get_absolute_url(url)
        if headers is None:
            headers = {}
        headers['Timestamp'] = str(int(time.time()) - EPOCH)
        if 'data' in kwargs:
            headers['Content-Type'] = 'application/json'
        try:
            response = super(_Session, self).request(method, url, headers=headers, **kwargs)
        except requests.exceptions.ConnectionError:
            logging.getLogger('verbose').exception('Failed to connect to {}'.format(url))
            raise CommandError('Failed to connect to server')
        logger.debug('HTTP {}\n{!r}\n----------\n{!r}\n----------'
                     .format(response.status_code, response.headers, response.content[:0x10000]))
        try:
            timestamp = float(response.headers['Timestamp'])
        except KeyError:
            raise CommandError('Invalid response (no Timestamp header)')
        if abs(time.time() - EPOCH - timestamp) > MAX_TIMESTAMP_DELTA:
            raise CommandError('Invalid response (Timestamp is different {!r} vs {!r})'
                               .format(timestamp, time.time() - EPOCH))
        if 'Digest' in response.headers:
            try:
                if not compare_digest(response.content, response.headers['Digest']):
                    raise CommandError('Invalid response (Digest header does not match the body)')
            except InvalidDigest:
                raise CommandError('Invalid response (Digest header is invalid)')
        if response.status_code >= 400 and not (allow_404 and response.status_code == 404):
            try:
                detail = response.json()['detail']
            except Exception:
                detail = response.text
            message = 'HTTP Error {}'.format(response.status_code)
            if detail:
                message += ': ' + detail
            raise CommandError(message)
        return response


def _get_session():
    key_id, secret = read_key()
    return _Session(key_id, secret)


def replace_tags(function):
    """
    Decorator to automatically translate tags to hashes.

    Works for following arguments:
    - package_id
    - script_id
    """
    @functools.wraps(function)
    def replace_tags_decorator(**kwargs):
        logger = logging.getLogger('brief')
        # Are there any tags in arguments?
        params_to_replace = []
        for param in ('script_id', 'package_id', 'device_id', 'function_id'):
            value = kwargs.get(param)
            if value is not None and not HASH_REGEX.match(value):
                if not TAG_REGEX.match(value):
                    raise CommandError('Not a valid hash or tag: {}'.format(value))
                params_to_replace.append(param)
        # Replace tags with hashes
        if params_to_replace:
            with TagStore() as tagstore:
                for param in params_to_replace:
                    tag = kwargs[param]
                    hash = tagstore.get_hash(tag)
                    if hash is None:
                        raise CommandError('Tag not found: {}'.format(tag))
                    logger.debug('{} -> {}'.format(kwargs[param], hash))
                    kwargs[param] = hash
        # Finally, call the function
        return function(**kwargs)
    return replace_tags_decorator


def _encode_script_content(content):
    return b64encode(content).decode('latin1')


def upload(filename, module):
    """
    Upload file with filename to the cloud. It will be deployed to the devices as module.
    """
    try:
        with open(filename, 'rb') as file:
            script_data = file.read()
    except (IOError, OSError):
        raise CommandError('Failed to read {}'.format(filename))
    data = {
        'name': module,
        'content': _encode_script_content(script_data)
    }
    session = _get_session()
    response = session.post('/scripts/', json=data)
    data = response.json()
    print(data['id'])


def list_scripts():
    """
    List the scripts that have been previously been uploaded to the Pozetron cloud.
    """
    session = _get_session()
    response = session.get('/scripts/')
    data = response.json()
    _print_ids(data)


def _print_ids(data):
    """Print d['id'] for each element of data, and also print tags."""
    with TagStore() as tagstore:
        for item in data:
            tags = tagstore.get_tags(item['id'])
            if tags:
                print('{} <- {}'.format(item['id'], ', '.join(tags)))
            else:
                print(item['id'])


@replace_tags
def rm_script(script_id):
    """
    Remove the script from the cloud.
    This will also result in the script being removed from any devices that it is deployed on
    the next time those devices check in.
    """
    session = _get_session()
    response = session.delete('/scripts/{}/'.format(script_id), allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Script not found')


def _collect_package_files(dirname, ignore_data_files=False):
    """
    Collect files within a package and return list
    [{"name": <relative_path>, "content": <bytes>}].
    """
    root = op.abspath(op.join(dirname, '..'))
    if not any(op.isfile(op.join(dirname, '__init__' + x)) for x in _PYTHON_EXTENSIONS):
        raise CommandError(problem='Not a Python package (no __init__.{})'
                                   .format('|'.join(x.lstrip('.') for x in _PYTHON_EXTENSIONS)))
    result = []
    non_python = []
    for current_root, dirname, filenames in os.walk(dirname):
        for filename in filenames:
            filepath = op.join(current_root, filename)
            if op.splitext(filename)[1] not in ('.py', '.mpy'):
                if op.splitext(filename)[1] == '.pyc':
                    pass
                else:
                    non_python.append(op.relpath(filepath, root))
                continue
            with open(filepath, 'rb') as file:
                result.append({
                    'name': op.relpath(filepath, root),
                    'content': file.read()
                })
    if non_python:
        if ignore_data_files:
            logger = logging.getLogger('brief')
            logger.info('Non-Python files ignored:\n{}'.format('\n'.join(non_python)))
        else:
            raise CommandError(problem='Non-Python files in the package are not supported:\n{}'
                                       .format('\n'.join(non_python)),
                               solution='Please remove the files '
                                        'or use --ignore-data-files option.')

    result.sort(key=lambda x: x['name'])
    return result


def upload_package(dirname, package_name, ignore_data_files):
    """
    Upload a Python package to the cloud. It can be deployed to devices.
    """
    modules = _collect_package_files(dirname, ignore_data_files=ignore_data_files)
    # Prepare data
    for module in modules:
        module['content'] = _encode_script_content(module['content'])
    # Upload package
    session = _get_session()
    response = session.post('/packages/', json={
        'name': package_name,
        'modules': modules
    })
    print(response.json()['id'])


def list_packages():
    """
    List the packages that have been previously been uploaded to the Pozetron cloud.
    """
    session = _get_session()
    response = session.get('/packages/')
    data = response.json()
    _print_ids(data)


@replace_tags
def describe_package(package_id):
    """
    Print package details.
    """
    session = _get_session()
    response = session.get('/packages/{}/'.format(package_id), allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Package not found')
        return
    data = response.json()
    print(data['name'])
    print('Files:')
    for module in data['modules']:
        print(module['name'])


@replace_tags
def rm_package(package_id):
    """
    Remove the package from the cloud, including all associated modules.
    This will also result in all modules being removed from devices,
    the next time those devices check in.
    """
    session = _get_session()
    response = session.delete('/packages/{}/'.format(package_id), allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Package not found')


def provision(hmac_key):
    """
    Provision a new device in the cloud using the provided hmac_key.
    This will return a new device id in the form of an email address,
    as well as a key_id which is used with the hmac_key to authenticate the device.
    """
    session = _get_session()
    response = session.post('/devices/', json={
        'hmac_key': hmac_key,
    })
    _print_provision(response.json())


def _print_provision(data):
    print('{}@pozetrondevices.com'.format(data['id']))
    print('{}'.format(data['keyId']))


def claim(code):
    """
    Claim a pre-provisioned device using a device code.
    The result is the same as provision.
    """
    session = _get_session()
    response = session.put('/devices/{}/claim/'.format(code), allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')
        return
    _print_provision(response.json())


def list_devices():
    """
    Generate a list of devices that are currently provisioned in the cloud.
    """
    session = _get_session()
    response = session.get('/devices/')
    data = response.json()
    with TagStore() as tagstore:
        for device in data:
            s = '{}@pozetrondevices.com'.format(device['id'])
            tags = tagstore.get_tags(device['id'])
            if tags:
                s += ' <- {}'.format(', '.join(tags))
            print(s)
            print(device['keyId'])


@replace_tags
def deprovision(device_id):
    """
    Remove the device from the cloud.
    """
    session = _get_session()
    response = session.delete('/devices/{}/'.format(device_id), allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')


@replace_tags
def deploy(script_id, device_id):
    """
    Deploy the script with `script_id` to the device with `device_id`.
    The script will be written to the device next time it checks in.
    """
    session = _get_session()
    response = session.post('/devices/{}/scripts/'.format(device_id),
                            json={'id': script_id},
                            allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')


@replace_tags
def undeploy(script_id, device_id):
    """
    Undeploy the script with script_id from the device with device_id.
    This will remove the script from the device next time it checks in.
    """
    session = _get_session()
    response = session.delete('/devices/{}/scripts/{}/'.format(device_id, script_id),
                              allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found or script not deployed to device')


@replace_tags
def list_deployed(device_id):
    """
    This will list the scripts which are currently deployed to the device with device_id.
    """
    session = _get_session()
    response = session.get('/devices/{}/scripts/'.format(device_id), allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')
        return
    data = response.json()
    _print_ids(data)


@replace_tags
def deploy_package(package_id, device_id):
    """
    Deploy the package with `package_id` to the device with `device_id`.
    Package modules be written to the device next time it checks in.
    """
    session = _get_session()
    response = session.post('/devices/{}/packages/'.format(device_id),
                            json={'id': package_id},
                            allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')


@replace_tags
def undeploy_package(package_id, device_id):
    """
    Undeploy the script with script_id from the device with device_id.
    This will remove the script from the device next time it checks in.
    """
    session = _get_session()
    response = session.delete('/devices/{}/packages/{}/'.format(device_id, package_id),
                              allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found or package not deployed to device')


@replace_tags
def list_deployed_packages(device_id):
    """
    This will list the packages which are currently deployed to the device with device_id.
    """
    session = _get_session()
    response = session.get('/devices/{}/packages/'.format(device_id), allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')
        return
    data = response.json()
    _print_ids(data)


@replace_tags
def download_firmware(device_id, device_type):
    """
    This will download the custom firmware for the device with the credentials for the
    Pozetron cloud embedded.
    """
    session = _get_session()
    response = session.get('/devices/{}/firmware/?type={}'.format(device_id, device_type), allow_404=True)
    if response.status_code == 404:
        if 'Firmware not found' in response.json()['detail']:
            raise CommandError('Firmware not found')
        logging.getLogger('brief').info('Device not found')
        return
    data = response.json()
    try:
        response = requests.get(data['url'], stream=True)
        with open(data['firmware_filename'], 'wb') as local_file:
            shutil.copyfileobj(response.raw, local_file)
        print(data['firmware_filename'])
    except requests.RequestException:
        logging.getLogger('verbose').exception('Failed GET {}'.format(data['url']))
        raise CommandError('Error downloading firmware file')


@replace_tags
def provision_function(script_id):
    print('NOT IMPLEMENTED')  # pragma: no cover


@replace_tags
def deprovision_function(function_id):
    print('NOT IMPLEMENTED')  # pragma: no cover


@replace_tags
def deploy_function(function_id, device_id):
    print('NOT IMPLEMENTED')  # pragma: no cover


@replace_tags
def undeploy_function(function_id, device_id):
    print('NOT_IMPLEMENTED')  # pragma: no cover


@replace_tags
def reboot(device_id):
    """
    This initiates a reboot the next time the device checks in.
    """
    session = _get_session()
    response = session.post('/devices/{}/reboot/'.format(device_id), allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')


@replace_tags
def forget_network(device_id):
    """Forget the network settings."""
    session = _get_session()
    response = session.post('/devices/{}/forget-network/'.format(device_id), allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')


@replace_tags
def last_seen(tz_name, device_id):
    """
    This command returns the timestamp that the device with device_id
    last checked in with the cloud.
    """
    session = _get_session()
    response = session.get('/devices/{}/last-seen/'.format(device_id), allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')
        return
    data = response.json()
    timestamp = data['time']
    if timestamp == 0:
        print('No data')
        return
    if not tz_name.lower() == 'unix':
        try:
            tz = get_timezone(tz_name)
            dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.UTC).astimezone(tz)
            print(dt.strftime('%Y-%m-%d %H:%M:%S'))
        except ValueError as ex:
            raise CommandError(str(ex))
    else:
        print(timestamp)


@replace_tags
def log_mode(device_id, enable, mode=None, file_size=None):
    """
    Enables or disables the log mode on the device with device_id.
    Next time the device checks in, all print methods will be directed
    to the cloud and can be retrieved from the command line client.
    """
    session = _get_session()
    if enable not in ('enable', 'disable'):
        raise ValueError('Unexpected argument: {!r}'.format(enable))  # pragma: nocover
    data = {'enable': enable == 'enable'}
    if mode is not None:
        if mode not in ('file', 'memory'):
            raise ValueError('Unexpected argument: {!r}'.format(mode))  # pragma: nocover
        data['mode'] = mode
    if file_size is not None:
        data['file_size'] = file_size
    response = session.post('/devices/{}/log-mode/'.format(device_id), json=data, allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')


@replace_tags
def logs(device_id, timestamp):
    """
    Returns the logs for the device with device_id,
    optionally from the point in time specified by timestamp.
    """
    session = _get_session()
    url = '/devices/{}/logs/'.format(device_id)
    if timestamp:
        url += '?from={}'.format(timestamp)
    response = session.get(url, allow_404=True)
    if response.status_code == 404:
        logging.getLogger('brief').info('Device not found')
        return
    for item in response.json():
        print('{} {}'.format(item['timestamp'], item['text']))


def add_tag(hash, tag):
    """Associate tag with a given hash. Tags are stored locally."""
    try:
        with TagStore() as tagstore:
            tagstore.add_tag(hash, tag)
    except TagError as ex:
        raise CommandError(problem=str(ex))


def remove_tag(tag):
    try:
        with TagStore() as tagstore:
            tagstore.remove_tag(tag)
    except TagError as ex:
        raise CommandError(str(ex))
