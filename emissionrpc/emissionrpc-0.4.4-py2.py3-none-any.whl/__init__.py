
"""
emissionrpc Library
~~~~~~~~~~~~~~~~~~~~~
Wrapper JSON-RPC for transmission.

usage:
   >>> import emission
   >>> c = emissionrpc.Client()
   >>> c.list_torrent()
"""

from .helpers import check_ids
from .exceptions import EmissionException, EmissionBadParameter, EmissionLibError
from .server import Server
from .emitter import Client
