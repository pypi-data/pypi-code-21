__version__ = '0.0.1'

from .config import Config
from .logging import Logger

config = None
logger = None


def start(name, config_path=None):
    global config, logger
    config = Config(name, config_path)
    logger = Logger(name)
