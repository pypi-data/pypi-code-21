import os.path
import yaml
import logging

logger = logging.getLogger(__name__)

class Config(object):
    """Gets configuration data from a config file"""
    def __init__(self, configFile):
        """Initialize the config object
        
        Args:
            configFile (str): Path to the configuration file
        """
        if os.path.isfile(configFile):
            self.parseConfig(configFile)
        else:
            logger.error("Config file {} does not exist".format(configFile))
            raise IOError("File {} does not exist".format(configFile))
        
    def parseConfig(self, configFile):
        with open(configFile, 'r') as f:
            config = yaml.safe_load(f)
            #logger.debug("Dump of configuration:{}".format(config))
            self.__dict__.update(**config)
            