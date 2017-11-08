'''A simple implementation for BatchCompute service SDK.
'''
__version__ = '2.0.9a2'
__all__ = [
    "Client", "ClientError", "FieldError", "ValidationError", "JsonError",
    "ConfigError", "CN_QINGDAO", "CN_HANGZHOU", "CN_SHENZHEN", "CN_BEIJING",
]
__author__ = 'crisish'

from .client import Client
from .core import ClientError, FieldError, ValidationError, JsonError
from .utils import CN_QINGDAO, CN_HANGZHOU, CN_SHENZHEN, CN_BEIJING, ConfigError
