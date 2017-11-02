"""
Mailer backend that writes email messages to the console instead of sending
them.
"""

import os
import pathlib
import sys
import threading

from manhattan.mail import EmailTemplate
from manhattan.mail.backends.base import BaseMailer

__all__ = ['Mailer']


class Mailer(BaseMailer):
    """
    Mailer that writes emails messages to file.

    This backend is provided to help developers review emails before
    production, each email sent overrides the contents of a single file.
    """

    def __init__(self, file_path=None, *args, **kwargs):
        self.file_path = file_path
        self._lock = threading.RLock()

        assert self.file_path, 'A `file_path` must be specified'

        super().__init__(*args, **kwargs)

    def send(self, messages):
        """Write each email messages to a file given by the file path"""
        if isinstance(messages, EmailTemplate):
            messages = messages.merge()

        # Split the file path into a directory path and filename
        dir_path, filename = os.path.split(self.file_path)

        # Make sure the save directory exists
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)

        message_count = 0

        with self._lock:
            try:
                for message in messages:
                    with open(self.file_path, 'w') as f:
                        self._write_message(f, message)

                    message_count += 1
            except Exception:
                if not self.fail_silently:
                    raise

        return message_count

    def _write_message(self, file, message):
        """Write a message to the stream"""
        msg_data = message.message.as_bytes()
        msg_data = msg_data.decode(message.encoding)
        file.write('%s\n' % msg_data)
        file.write('-' * 79)
        file.write('\n')
