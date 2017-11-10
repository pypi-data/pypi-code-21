# -*- coding: utf-8 -*-

"""
Enhance error management for environment variables
"""

import os


def env2(key, default=None, raise_error=True):
    """Return an environment variable or default,
        raise_error if you want to stop your program.
    """
    var = os.environ.get(key, default)
    if not var:
        msg = '{0} not found in environment variables'.format(key)
        print(msg)
        if raise_error:
            raise Exception('{0} not found in environment variables'.format(key))
    return var


if __name__ == '__main__':
    x = env2('FORK_USER', raise_error=True)
    print(x)
