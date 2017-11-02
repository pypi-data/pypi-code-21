"""
Classes for implementing a backend for asset management.
"""

import json

__all__ = ['BaseMailer']


# Classes

class BaseMailer:
    """
    Email is sent out by via a mailer class which must provide the API defined
    by the `BaseMailer` class.
    """

    def __init__(self, fail_silently=False, **kwargs):
        # Flag indicating if exceptions raised while sending email messages
        # should be ignored.
        self.fail_silently = fail_silently

    def __enter__(self):
        try:
            self.open()
        except Exception:
            self.close()
            raise
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self):
        """Open a connection to the email server/service"""

    def close(self):
        """Close connection to the email server/service"""

    def send(self, messages):
        """
        Send a list of email messages. The `email_messages` argument can either
        be defined as a list of `EmailMessage` instances or an `EmailTemplate`
        instance.
        """
        raise NotImplementedError('Must be overridden by inheriting classes')
