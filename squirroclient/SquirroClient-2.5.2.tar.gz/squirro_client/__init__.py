"""This root level directives are imported from submodules. They are made
available here as well to keep the number of imports to a minimum for most
applications.
"""
__version__ = '2.5.2'

from .base import SquirroClient
from .exceptions import *
from .item_uploader import ItemUploader
from .document_uploader import DocumentUploader
