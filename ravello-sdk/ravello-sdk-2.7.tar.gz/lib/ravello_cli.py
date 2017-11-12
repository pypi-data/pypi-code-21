# Copyright 2012-2014 Ravello Systems, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, print_function

import os
import re
import sys
import logging
import socket
import six

from getpass import getpass
from six.moves import reduce

from ravello_sdk import RavelloClient, RavelloError


common_options = """\
Common options:
  -d, --debug       Enable debugging mode.
  -u <username>, --username <username>
                    Ravello API username ($RAVELLO_USERNAME)
  -p <password>, --password <password>
                    Ravello API password ($RAVELLO_PASSWORD)
"""

def parse_common_arguments(args):
    """Check arguments common to all CLI programs."""
    values = {}
    values['debug'] = bool(args.get('--debug'))
    username = args['--username']
    if not username:
        username = os.environ.get('RAVELLO_USERNAME')
        if username is None:
            raise ValueError('missing -u/--username or $RAVELLO_USERNAME')
    values['username'] = username
    password = args['--password']
    if not password:
        password = os.environ.get('RAVELLO_PASSWORD')
        if password is None and not sys.stdin.isatty():
            raise ValueError('missing -p/--password or $RAVELLO_PASSWORD')
    values['password'] = password
    return values


def validate_bool_arg(args, name):
    """Validate a boolean argument."""
    value = args.get(name) if isinstance(args, dict) else args
    if not value:
        return False
    if value.lower() in ('n', 'no', '0', 'off', 'disabled'):
        return False
    elif value.lower() in ('y', 'yes', '1', 'on', 'enabled'):
        return True
    raise ValueError('invalid boolean for {0}: {1}'.format(name, value))


def validate_int_arg(args, name, low=None, high=None):
    """Validate an integer command-line argument."""
    value = args.get(name) if isinstance(args, dict) else args
    if not value:
        return 0
    try:
        intval = int(value)
    except ValueError:
        raise ValueError('invalid integer for {0}: {1}'.format(name, value))
    if low is not None and intval < low:
        raise ValueError('invalid value for {0}: minimum is {1}, got {2}'
                            .format(name, low, value))
    if high is not None and intval > high:
        raise ValueError('invalid value for {0}: maximum is {1}, got {2}'
                            .format(name, high, value))
    return intval


def _validate_suffix_arg(suffixes, args, name, default_suffix, low=None, high=None):
    # Validate an argument with a suffix.
    value = args.get(name) if isinstance(args, dict) else args
    if not value:
        return
    if value.isdigit():
        base = value
        suffix = default_suffix
    else:
        base = value[:-1]
        suffix = value[-1:]
        if suffix not in suffixes:
            raise ValueError('illegal suffix for {0}: {1}'.format(name, suffix))
    try:
        base = int(base)
    except ValueError:
        raise ValueError('invalid value for {0}: {1}'.format(name, value))
    converted = base * suffixes[suffix]
    if low is not None and converted < low * suffixes[default_suffix]:
        raise ValueError('invalid value for {0}: minimum is {1}{2}, got {3}'
                            .format(name, low, default_suffix, value))
    if high is not None and converted < high * suffixes[default_suffix]:
        raise ValueError('invalid value for {0}: maximum is {1}{2}, got {3}'
                            .format(name, high, default_suffix, value))
    return converted


_size_suffixes = {'M': 2**20, 'G': 2**30}

def validate_size_arg(args, name, default_suffix, low=None, high=None):
    """Validate a size argument. Supports 'M' (MB) and 'G' (GB) suffixes."""
    return _validate_suffix_arg(_size_suffixes, args, name, default_suffix, low, high)


_interval_suffixes = {'M': 60, 'H': 3600}

def validate_interval_arg(args, name, default_suffix, low=None, high=None):
    """Validate a interval argument. Supports 'M' (minute) and 'H' (hour) suffixes."""
    return _validate_suffix_arg(_interval_suffixes, args, name, default_suffix, low, high)


def validate_enum_arg(args, name, choices, allow_query=True):
    """Validate an enum argument."""
    value = args.get(name) if isinstance(args, dict) else args
    if not value:
        return
    if value == '?' and allow_query:
        return value
    lcase = value.lower()
    if lcase not in choices:
        raise ValueError('invalid value for {0}: {1}'.format(name, value))
    return lcase


def validate_network_arg(args, name):
    """Validate a network argument. Can be either 'dhcp' or network/bits."""
    value = args.get(name) if isinstance(args, dict) else args
    if not value:
        return
    if value == 'dhcp':
        return value
    try:
        parsed = parse_cidr(value)
    except ValueError:
        raise ValueError('invalid value for {0}: {1}'.format(name, value))
    return parsed


re_range = re.compile('^\d+-\d+$')

def validate_service_arg(args, name):
    """Validate a service argument. Can be either a port number, a port range,
    or a symbolic service name from /etc/services."""
    value = args.get(name) if isinstance(args, dict) else args
    if value.isdigit():
        port = int(value)
        if not 1 <= port < 65536:
            raise ValueError('illegal port number for {0}: {1}'.format(name, value))
        try:
            name = socket.getservbyport(port)
        except socket.error:
            name = 'p-{0}'.format(port)
    elif re_range.match(value):
        start, end = map(int, value.split('-'))
        if not 1 <= start < 65536 or not 1 <= end < 65536 or end <= start:
            raise ValueError('illegal port range for {0}: {1}'.format(name, value))
        name = 'r-{0}+{1}'.format(start, end-start)
    else:
        name = value
        try:
            value = socket.getservbyname(name)
        except socket.error:
            raise ValueError('unknown service for {0}: {1}'.format(name, value))
    return (name, value)


def expand_multival_arg(args, name, count):
    """Expand a "multival" argument."""
    value = args.get(name)
    if value is None:
        raise ValueError('missing value for {0}'.format(name))
    parts = value.split(',')
    if len(parts) < count:
        parts += [parts[-1]] * (count - len(parts))
    elif len(parts) > count:
        parts = parts[:count]
    return parts


def mac_aton(s):
    """Convert a Mac address to an integer."""
    try:
        mac = list(map(lambda x: int(x, 16), s.split(':')))
        mac = reduce(lambda a,b: a+b, [mac[i] << (5-i)*8 for i in range(6)])
    except (ValueError, IndexError):
        raise ValueError('illegal Mac: {0}'.format(s))
    return mac


def mac_ntoa(i):
    """Convert an int to a mac address."""
    return ':'.join(map(lambda x: '%02x'%x, [(i >> (5-j)*8) & 0xff for j in range(6)]))


def inet_aton(s):
    """Convert a dotted-quad to an int."""
    try:
        addr = list(map(int, s.split('.')))
        addr = reduce(lambda a,b: a+b, [addr[i] << (3-i)*8 for i in range(4)])
    except (ValueError, IndexError):
        raise ValueError('illegal IP: {0}'.format(s))
    return addr


def inet_ntoa(i):
    """Convert an int to dotted quad."""
    return '.'.join(map(str, [(i >> (3-j)*8) & 0xff for j in range(4)]))


def parse_cidr(network):
    """Parse a address/bits CIDR type network address."""
    try:
        addr, bits = network.split('/')
        addr = inet_aton(addr)
        bits = int(bits)
        if not 0 <= bits <= 32:
            raise ValueError
    except ValueError:
        raise ValueError('illegal network: {0}'.format(network))
    netmask = (0xffffffff << (32 - bits)) & 0xffffffff
    network = addr & netmask
    return inet_ntoa(network), inet_ntoa(netmask)


def getservbyport(port):
    """Like socket.getservbyport() but return a descriptive string if the
    service is not found."""
    try:
        name = socket.getservbyport(port)
    except socket.error:
        name = 'port-{0}'.format(port)
    return name


def getservbyname(name):
    """Like socket.getservbyname() but return a ValueError with a descriptive
    message if the ser4vice is not found."""
    try:
        port = socket.getservbyname(name)
    except socket.error:
        raise ValueError('unknown service: {0}'.format(name))
    return port


def setup_logger(debug):
    """Setup the logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    logger.addHandler(handler)
    return logger


# API methods

def create_client(args):
    """Connect to the Ravello API and return a connection."""
    client = RavelloClient()
    if args['password'] is None:
        args['password'] = getpass('Enter password for {0}: '.format(args['username']))
    client.connect()
    try:
        client.login(args['username'], args['password'])
    except RavelloError:
        raise RavelloError('could not login with provided credentials')
    return client


def get_image(client, name_or_id):
    """Load an image by name or ID."""
    if name_or_id.isdigit():
        return client.get_image(name_or_id)
    images = client.get_images({'name': name_or_id})
    if not images:
        return
    return client.reload(images[0])


def get_diskimage(client, name_or_id):
    """Load a disk image by name or ID."""
    if name_or_id.isdigit():
        return client.get_diskimage(name_or_id)
    images = client.get_diskimages({'name': name_or_id})
    if not images:
        return
    return client.reload(images[0])


def get_application(client, name_or_id):
    """Load an application by name or ID."""
    if name_or_id.isdigit():
        return client.get_application(name_or_id)
    applications = client.get_applications({'name': name_or_id})
    if not applications:
        return
    return client.reload(applications[0])


def get_keypair(client, name_or_id):
    """Load a keypair by name or ID."""
    if name_or_id.isdigit():
        return client.get_keypair(name_or_id)
    keypairs = client.get_keypairs({'name': name_or_id})
    if not keypairs:
        return
    return client.reload(keypairs[0])


def new_name(prefix, existing):
    """Return a name that starts with *prefix* and is not in *existing*."""
    if not isinstance(prefix, six.text_type):
        prefix = prefix.decode('ascii')
    for i in range(len(existing)+1):
        name = u'{0}-{1}'.format(prefix, i)
        if name not in existing:
            break
    existing.add(name)
    return name
