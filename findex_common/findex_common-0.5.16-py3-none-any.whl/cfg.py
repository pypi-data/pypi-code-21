import os
import sys
import inspect

from backports import configparser as ConfigParser

import appdirs
from findex_common.exceptions import ConfigError, ConfigNotFoundError


class Config:
    def __init__(self, filename='config'):
        self._items = {}
        self._last_accessed = None
        self._filename = filename

        self.reload()

    def __getitem__(self, item):
        if item not in self._items:
            raise ConfigError('Required block \'%s\' not found in config file \'%s\'.' % (item, self._filename))
        return self._items[item]

    def reload(self):
        system_path = os.path.join(appdirs.site_config_dir('findex'), self._filename)
        user_path = os.path.join(appdirs.user_config_dir('findex'), self._filename)

        if not os.path.isfile(system_path) and not os.path.isfile(user_path):
            raise ConfigNotFoundError('Could not load config file \'%s\' or \'%s\'.' % (user_path, system_path))

        cfg = ConfigParser.ConfigParser()
        cfg.read([system_path, user_path])

        data = {}
        for section in cfg.sections():
            data[section] = {}

            for k, v in cfg.items(section):
                if k.startswith('#') or v.startswith('#'):
                    continue

                if v:
                    try:
                        data[section][k] = int(v) if'.' not in v else float(v)
                        continue
                    except:
                        pass

                    if v.lower() == 'false':
                        data[section][k] = False
                        continue
                    elif v.lower() == 'true':
                        data[section][k] = True
                        continue

                data[section][k] = v

        self._validate_cfg(data)
        self._items = data

    def _validate_cfg(self, data):
        required = {
            'gui.cfg': {
                'general': [
                    'debug',
                    'bind_host',
                    'bind_port'
                ],
                'database': [
                    'hosts',
                    'port',
                    'database',
                    'username',
                    'password'
                ]
            },
            'crawl.cfg': {
                'general': [
                    'debug',
                    'queue_size'
                ],
                'database': [
                    'host',
                    'port',
                    'database',
                    'username',
                    'password'
                ],
                'rabbitmq': [
                    'username',
                    'password',
                    'vhost',
                    'host'
                ],
            }
        }

        if self._filename in required:
            if sys.hexversion >= 0x03050000:
                require = required[self._filename].items()
            else:
                require = required[self._filename].iteritems()

            for k, v in require:
                if k not in data:
                    raise ConfigError('Required block \'%s\' not found in config file \'%s\'.' % (k, self._filename))

                for a in v:
                    if a not in data[k]:
                        raise ConfigError('Required variable \'%s\' not found in block \'%s\' in config file \'%s\'.' % (
                            a, k, self._filename))

    def get(self, section, item):
        try:
            return self._items[section][item]
        except:
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            raise Exception('Could not access config variable \'%s\' from section \'%s\' - Caller: %s' % (
                item, section, mod.__name__))
