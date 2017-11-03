"""Exceptions raised explicitly in BreezeBlocks modules.

BreezeBlocks will use these when the module can easily predict that an error
would occur based on something passed to BreezeBlocks itself. An example of
this would be trying to instantiate a query without providing a database
argument.

Most database-related errors will still come from the underlying DBAPI module.
BreezeBlocks does not try to catch any mistakes you make in telling it about
your schema.
"""

class BreezeBlocksError(Exception):
    """Base class for all BreezeBlocks errors."""

class MissingModuleError(BreezeBlocksError):
    """An error occuring when a Database object would not have a DBAPI module.
    
    When a user does not provide a DBAPI module, the program will try to find
    one that it can use based on the DSN provided. This will fail if one of
    these conditions is met:
    
    1. The DSN does not correspond to DBAPI module known by BreezeBlocks.
    2. The correct DBAPI module cannot be imported.
    """
    
    def __repr__(self):
        return 'BreezeBlocks Error: No DBAPI module provided or detected.'

class QueryError(BreezeBlocksError):
    """An error occuring during creation of a query."""
    
    def __init__(self, message):
        self._message = message
    
    def __repr__(self):
        return 'BreezeBlocks Query Error: {}'.format(self._message)
