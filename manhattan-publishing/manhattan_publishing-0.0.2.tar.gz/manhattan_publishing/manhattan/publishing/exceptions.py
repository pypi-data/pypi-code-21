__all__ = ['PublishingError']


class PublishingError(Exception):
    """
    The base exception class for all errors raised when flagging an error in
    attempting to validate that it's possible to publish a document, see:
    `PublishableFrame.validate_publish`.
    """
