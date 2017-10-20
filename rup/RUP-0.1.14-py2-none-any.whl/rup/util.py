import re
import os.path
import errno
import os
import sys
import hashlib

import logging
import yaml

LMD_NUMBER_MATCH = re.compile(r"(\d+)_(\d+)\.lmd(\.gz)?")
RUP_NUMBER_MATCH = re.compile(r"(\d+)_rup\.yml")
LOG_NUMBER_MATCH = re.compile(r"(\d+)\.log")


def determine_run_number(path):
    path = os.path.basename(path)

    if is_data(path):
        pattern = LMD_NUMBER_MATCH
    elif is_rup(path):
        pattern = RUP_NUMBER_MATCH
    elif is_log(path):
        pattern = LOG_NUMBER_MATCH
    else:
        raise ValueError("Unknown file type {}".format(path))

    m = re.match(pattern, path)

    if m is None:
        return None

    return int(m.group(1))


def is_run_log(path):
    return path.endswith('runs.log')


def is_data(path):
    return path.endswith('lmd.gz')


def is_rup(path):
    return path.endswith('rup.yml')


def is_log(path):
    return path.endswith('.log')


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


HASH_BUF_SIZE = 65536


def sha512_file(path):
    sha = hashlib.sha512()
    with open(path, 'rb') as f:
        while True:
            data = f.read(HASH_BUF_SIZE)
            if not data:
                break
            sha.update(data)

    return sha.hexdigest()


def load_yaml(path):
    with open(path, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as e:
            logger = logging.getLogger('load_yaml')
            logger.error("Failed loading {}: {}".format(path, e.message))