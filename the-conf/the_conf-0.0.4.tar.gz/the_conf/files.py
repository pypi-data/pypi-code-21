import json
import logging
from os.path import abspath, expanduser, splitext

import yaml

logger = logging.getLogger(__name__)


def read(*paths):
    for path in paths:
        path = abspath(expanduser(path.strip()))
        ext = splitext(path)[1][1:]
        try:
            if ext in {'yml', 'yaml'}:
                with open(path, 'r') as fd:
                    yield path, ext, yaml.load(fd.read())
            elif ext == 'json':
                with open(path, 'r') as fd:
                    yield path, ext, json.load(fd)
            else:
                logger.error("File %r ignored: unknown type (%s)", path, ext)
                continue
        except FileNotFoundError:
            logger.warning('%r not found', path)
        except PermissionError:
            logger.warning('%r: no right to read', path)


def _extract_value(config, path):
    if path[0] in config and len(path) == 1:
        return config[path[0]]
    elif path[0] in config:
        return _extract_value(config[path[0]], path[1:])
    else:
        raise ValueError('no %r in %r' % (path[0], config))


def extract_values(paths, config, config_file):
    for path in paths:
        try:
            yield path, _extract_value(config, path)
        except ValueError:
            logger.info('%s not found in %r', '.'.join(path), config_file)


def write(config, path):
    path = abspath(expanduser(path.strip()))
    ext = splitext(path)[1][1:]
    if ext in {'yml', 'yaml'}:
        with open(path, 'w') as fp:
            yaml.dump(config, fp)
    elif ext == 'json':
        with open(path, 'w') as fp:
            json.dump(config, fp)
    else:
        raise ValueError("couldn't make out file type, conf file path should "
                         "end with either yml, yaml or json")
