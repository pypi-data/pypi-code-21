__version__ = '0.2.0'

from .config import Config, update_config
from .logging import Logger

config = None
logger = None


def start(name, config_path=None, config_variant='config'):
    global config, logger
    config = Config(name, config_path, variant=config_variant)
    logger = Logger(name)
