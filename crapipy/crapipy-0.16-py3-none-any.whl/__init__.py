"""
Clash Royale wrapper for cr-api.com
"""
__version__ = "0.16"

from .client import Client
from .client_async import AsyncClient
from .exceptions import APITimeoutError, APIClientResponseError, APIError
from .url import APIURL
