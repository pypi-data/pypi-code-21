from configobj import ConfigObj
import os


def setup(username, key, **kwargs):
    config_file_location = os.path.expanduser('~/.passivetotal2.cfg')
    config = ConfigObj(config_file_location)
    config['USERNAME'] = username
    config['APIKEY'] = key
    config.write()
    return "config file successfully written"
