"""WSGI middleware that loads auth0 config from a YAML file.

The YAML file name is configured with the
`wsgiauth0.clients_config_file` settings key.

The expected YAML format is a dictionary of clients, where the key is
a label.

    Client 1:
        id: oZ0ahm4Thoh1Oghiqu4oe9qu
        audience: oZ0ahm4Thoh1Oghiqu4oe9qu
        secret:
            value: noh4feibaighikeeD0inah9Rei3nei6yeenoa7
            type: base64_url_encoded

"""
import logging

import yaml

from .exception import Error

log = logging.getLogger(__name__)

clients_config_file_key = 'clients_config_file'


def has_yaml_config(config):
    return clients_config_file_key in config


def config_yaml(config):
    log.info('wsgiauth0 yaml configuration')
    if has_yaml_config(config):
        clients = client_settings_from_yaml(config)
        log.debug('yaml configured clients: %s', clients)
        return clients
    else:
        return {}


def client_settings_from_yaml(config):
    try:
        yaml_config_path = config[clients_config_file_key]
    except (KeyError, TypeError):
        raise Error(
            'missing_config',
            '"%s" key not found in config' % clients_config_file_key,
        )
    try:
        with open(yaml_config_path) as f:
            settings = yaml.load(f)
    except Exception:
        raise Error(
            'invalid_config_file',
            'Not able to read yaml data from file path="%s"'
            % yaml_config_path,
        )

    try:
        client_settings = settings.items()
    except AttributeError:
        raise Error(
            'invalid_config_format',
            'Expects a top level dict, got %s.' % type(settings),
        )
    return client_settings
