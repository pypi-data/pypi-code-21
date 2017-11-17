__all__ = ["InvalidMessage", "InvalidBlockSize"]

class InvalidMessage(Exception):
    """The message was not padded with the algorithm chosen"""

class InvalidBlockSize(Exception):
    """The block size provided is not supported by the padding algorithm"""
