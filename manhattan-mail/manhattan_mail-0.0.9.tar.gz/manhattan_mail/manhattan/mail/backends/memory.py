"""
Mailer backend that writes email messages to a buffer (list) instead of sending
them. Useful for testing.
"""

import threading

from manhattan.mail import EmailTemplate
from manhattan.mail.backends.base import BaseMailer

__all__ = ['Mailer']


class Mailer(BaseMailer):
    """
    Mailer that writes emails to a buffer (list).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = threading.RLock()

        if not hasattr(self.__class__, 'outbox'):
            self.__class__.outbox = []

    def clear(self):
        """Clear the outbox"""
        if hasattr(self.__class__, 'outbox'):
            self.__class__.outbox = []

    def send(self, messages):
        """Write all email messages to the buffer"""
        if isinstance(messages, EmailTemplate):
            messages = messages.merge()

        message_count = 0

        with self._lock:
            for message in messages:
                self.__class__.outbox.append(message.message)
                message_count += 1

        return message_count
