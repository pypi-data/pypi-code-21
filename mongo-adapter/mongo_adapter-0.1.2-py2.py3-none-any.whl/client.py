"""
client.py

Establish a connection to the database

"""
import logging

from pymongo import MongoClient
from pymongo.errors import (ConnectionFailure, ServerSelectionTimeoutError)

from .exceptions import InterfaceError

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus

LOG = logging.getLogger(__name__)

def check_connection(client):
    """Check if the mongod process is running
    
    Args:
        client(MongoClient)
    
    Returns:
        bool
    """
    try:
        client.server_info()
    except ServerSelectionTimeoutError as err:
        raise InterfaceError("Seems like mongod is not running")
    
    return True


def get_client(host='localhost', port=27017, username=None, password=None,
              uri=None, mongodb=None, timeout=20):
    """Get a client to the mongo database

    Args:
        host(str): Host of database
        port(int): Port of database
        username(str)
        password(str)
        uri(str)
        timeout(int): How long should the client try to connect

    Returns:
        client(pymongo.MongoClient)

    """
    if uri is None:
        if username and password:
            uri = ("mongodb://{}:{}@{}:{}"
                   .format(quote_plus(username), quote_plus(password), host, port))
        else:
            uri = ("mongodb://{0}:{1}".format(host, port))

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout)
    except ServerSelectionTimeoutError as err:
        LOG.warning("Connection Refused")
        raise InterfaceError
    
    LOG.debug("Check if mongod is running")
    check_connection(client)

    LOG.info("Connection established")
    return client
