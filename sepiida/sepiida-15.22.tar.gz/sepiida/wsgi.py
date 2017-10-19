import logging

LOGGER = logging.getLogger(__name__)

def stabilize_werkzeug_iterator():
    """
    Once upon a time we created a bunch of microservices. These services often had to deal with problems.
    So we connected them to sentry to log those problems. That was great until we had to deal with the fact
    that werkzeug actually gets an OSError on the socket when a client does the following:

    1. Connect to the service.
    2. Request a resource
    3. Get disconnected, either by force or by choice, before the server sends all the data for the request

    What is going on is that the OS-level socket is now closed and we can't send data into it. This causes
    an OSError in the python level inside werkzeug. This is an unhandled exception. Because the connection
    is already closed it doesn't matter to werkzeug that this is an unhandled exception - the transaction
    is done no matter what. To us, with our integration with sentry, we *do* care because we treat all
    unhandled exceptions as programmer error. We are finally taking a stand and saying this is not *our*
    error.
    """
    import werkzeug.wsgi
    def stable_next(self):
        try:
            return self._next() # pylint: disable=protected-access
        except OSError as e:
            LOGGER.warning(
                "Caught OSError when iterating over WSGI socket (%s). "
                "This usually means the client disconnected before we were done sending them data.", e
            )
            raise StopIteration(str(e))
    werkzeug.wsgi.ClosingIterator.__next__ = stable_next
