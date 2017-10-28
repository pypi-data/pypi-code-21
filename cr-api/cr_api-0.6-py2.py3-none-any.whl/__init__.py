"""
Clash Royale wrapper for cr-api.com
"""
__version__ = "0.6"

from .client import Client
from .exceptions import APITimeoutError, APIClientResponseError, APIError
from .models.clan import Clan