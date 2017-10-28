"""
Clash Royale wrapper for cr-api.com
"""
__version__ = "0.8"

from .client_async import AsyncClient
from .client import Client
from .exceptions import APITimeoutError, APIClientResponseError, APIError
from .url import APIURL
from .models import Clan, Tag, Player, Constants