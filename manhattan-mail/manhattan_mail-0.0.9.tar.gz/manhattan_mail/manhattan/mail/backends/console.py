"""
Mailer backend that writes email messages to the console instead of sending
them.
"""

import sys
import threading

from manhattan.mail import EmailTemplate
from manhattan.mail.backends.base import BaseMailer

__all__ = ['Mailer']


class Mailer(BaseMailer):
    """
    Mailer that writes emails messages to the console.
    """

    def __init__(self, stream=None, *args, **kwargs):
        self.stream = stream or sys.stdout
        self._lock = threading.RLock()
        super().__init__(*args, **kwargs)

    def send(self, messages):
        """Write all email messages to the stream"""
        if isinstance(messages, EmailTemplate):
            messages = messages.merge()

        message_count = 0

        with self._lock:
            try:
                for message in messages:
                    self._write_message(message)
                    self.stream.flush()
                    message_count += 1
            except Exception:
                if not self.fail_silently:
                    raise

        return message_count

    def _write_message(self, message):
        """Write a message to the stream"""
        msg_data = message.message.as_bytes()
        msg_data = msg_data.decode(message.encoding)
        self.stream.write('%s\n' % msg_data)
        self.stream.write('-' * 79)
        self.stream.write('\n')
