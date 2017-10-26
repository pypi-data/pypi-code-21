from __future__ import absolute_import, unicode_literals

import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

_SECTIONS = ['ilabs', 'default']
_KEY     = 'ilabs_user_key'


def get_user_key():
    '''Implements strategy for obtaining user key from the runtime context:

    1. Environment variable ILABS_USER_KEY
    2. User config file in `~/.config/ilabs/ilabs.conf` (in `[ilabs]` section
        or `[default]` section)
    3. System-wide config file `/etc/ilabs.conf` (in `[ilabs]` section
       or `[default]` section)

    Sample config file:

        [default]
        ilabs_user_key=1234567890

    '''

    user_key = os.environ.get('ILABS_USER_KEY')
    if user_key is not None:
        return user_key

    config = configparser.ConfigParser()
    config.read([
        '/etc/ilabs.conf',
        os.path.expanduser(r'~/.config/ilabs/ilabs.conf')
    ])

    for section in _SECTIONS:
        try:
            user_key = config.get(section, _KEY)
            return user_key
        except configparser.NoSectionError:
            pass
        except configparser.NoOptionError:
            pass
