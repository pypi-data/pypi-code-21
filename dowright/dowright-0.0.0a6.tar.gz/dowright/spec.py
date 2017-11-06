import logging
import copy
from pathlib import Path
from typing import Union

# from ansible.inventory import expand_hosts
from . import ansible_expand_hosts as expand_hosts

from .yaml import read_yaml

log = logging.getLogger('spec')
log.addHandler(logging.NullHandler())


class DOWrightSpecError(Exception):
    pass


def verify_spec(spec:dict) -> dict:
    is_str = lambda v: type(v) is str
    is_dict = lambda v: hasattr(v, 'keys')

    required_keys = [
        ('token', is_str),
        ('prefix', is_str),
        ('droplets', is_dict),
    ]

    for key, func in required_keys:
        if key not in spec:
            raise DOWrightSpecError('Key: "%s" required in spec'.format(key))
        if not func(spec[key]):
            raise DOWrightSpecError(
                'Key: "%s" is not required type'.format(key)
            )

    return spec


def parse_spec(path:Union[Path,str]) -> dict:
    log.debug('Reading spec path: %s', path)
    spec = verify_spec(read_yaml(path))
    for dtype,configs in spec['droplets'].items():
        new_configs = []
        log.debug('Found %s configs for droplet type %s', len(configs), dtype)
        for config in configs:
            name = config['name']
            if expand_hosts.detect_range(name):
                log.debug('Found Ansible-style hostname range: %s', name)
                for new_name in expand_hosts.expand_hostname_range(name):
                    new_config = copy.deepcopy(config)
                    new_config['name'] = new_name
                    new_configs.append(new_config)
            else:
                new_configs.append(config)
        log.debug('%s total configs created for droplet type %s',
                  len(new_configs), dtype)
        spec['droplets'][dtype] = new_configs
    return spec
