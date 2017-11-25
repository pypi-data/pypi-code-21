import os
import json

import gease.exceptions as exceptions
import gease.constants as constants
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def get_info(key):
    """
    Find geasefile from user's home folder
    """
    home_dir = os.path.expanduser('~')
    geasefile = os.path.join(home_dir,
                             constants.DEFAULT_GEASE_FILE_NAME)
    try:
        with open(geasefile, 'r') as config:
            gease = json.load(config)
            return gease[key]
    except FileNotFoundError:
        raise exceptions.NoGeaseConfigFound(
            'Cannot find %s' % geasefile)
