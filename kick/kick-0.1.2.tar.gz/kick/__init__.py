__version__ = '0.1.2'

import inspect
import pathlib

from first import first

from .config import Config
from .logging import Logger

config = None
logger = None


def get_caller_path():
    stack = inspect.stack()
    try:
        frame = first(stack, key=lambda frame: 'kick.start(' in (frame.code_context[0] or ['']))
        return pathlib.Path(frame.filename).parent / 'config.toml'
    finally:
        del stack


def start(name, config_path=None):
    global config, logger
    config = Config(name, config_path or get_caller_path())
    logger = Logger(name)
