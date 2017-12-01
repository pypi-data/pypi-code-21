from accern import error

import ConfigParser
import os

__all__ = [
    'get_config'
]


def get_config(section):
    Config = ConfigParser.ConfigParser()
    if not os.path.exists('accern.ini'):
        raise error.ConfigError("Config file not find.")

    Config.read('accern.ini')
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except ValueError:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1
