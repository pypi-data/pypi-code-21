"""
Exceptions defined for pypad

InvalidMessage is raised when an invalid block has been given to an unpad function.
InvalidBlockSize is raised when an invalid block size has been provided.
"""

__all__ = ["InvalidMessage", "InvalidBlockSize"]

class InvalidMessage(Exception):
    """The message was not padded with the algorithm chosen"""

class InvalidBlockSize(Exception):
    """The block size provided is not supported by the padding algorithm"""
