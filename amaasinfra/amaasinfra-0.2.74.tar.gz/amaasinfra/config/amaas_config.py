import os
from configparser import ConfigParser, NoSectionError

class AMaaSConfig(object):
    def __init__(self, config_path=None):
        if not config_path:
            config_path = os.path.join(os.path.expanduser('~'), '.amaas.cfg')
        if not os.path.exists(config_path):
            raise Exception('Could not read AMaaS config file: {}'.format(config_path))
        self.config = ConfigParser()
        self.config.read(config_path)
    
    def get_config_value(self, section, option):
        if not self.config.has_section(section):
            raise Exception('Missing [{}] in AMaaS config file'.format(section))
        if not self.config.has_option(section, option):
            raise Exception('Missing {} optin in [{}] section of AMaaS config file'.format(section, option))
        
        return self.config.get(section=section, option=option)