import ConfigParser
import os
import sys


def get_config_dict(**kwargs):

    if not kwargs.get('config_file'):
        config_file = '%s/%s' % (os.getcwd(), 'generator.cfg')
    else:
        file_path = os.path.dirname(os.path.realpath(__file__))
        config_file = '%s/%s' % (file_path, kwargs.get('config_file'))

    config = ConfigParser.RawConfigParser()

    if not os.path.isfile(config_file):
        sys.exit("Expected to find configuration file with the setup")

    config.readfp(open(config_file))

    if not kwargs.get('section_key'):
        dirs_config_hash_map = config.items('dirs')
    else:
        dirs_config_hash_map = config.items(kwargs.get('section_key'))

    dirs_config_dict = {}

    for k, v in dirs_config_hash_map:
        dirs_config_dict[k] = v

    return dirs_config_dict


def get_constants_dict():
    return get_config_dict('constants.cfg')