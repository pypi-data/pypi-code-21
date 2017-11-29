import ConfigParser
import os
import sys


def get_config_dict(section_key=None):
    config = ConfigParser.RawConfigParser()

    config_file = '%s/%s' % (os.getcwd(), 'generator.cfg')

    if not os.path.isfile(config_file):
        sys.exit("Expected to find configuration file with the setup")

    config.readfp(open(config_file))

    if not section_key:
        dirs_config_hash_map = config.items('dirs')
    else:
        dirs_config_hash_map = config.items(section_key)

    dirs_config_dict = {}

    for k, v in dirs_config_hash_map:
        dirs_config_dict[k] = v

    return dirs_config_dict
