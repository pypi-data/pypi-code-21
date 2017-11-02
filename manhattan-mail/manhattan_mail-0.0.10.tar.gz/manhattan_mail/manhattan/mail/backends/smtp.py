"""
Mailer backend sends email via SMTP.
"""

import smtplib
import socket
import ssl
import threading

from manhattan.mail import EmailTemplate
from manhattan.mail.backends.base import BaseMailer

__all__ = ['Mailer']


class Mailer(BaseMailer):
    """
    SMTP mailer
    """

    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        use_tls=None,
        use_ssl=None,
        timeout=None,
        ssl_keyfile=None,
        ssl_certfile=None,
        *args,
        **kwargs
        ):
        super().__init__(*args, **kwargs)

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.ssl_keyfile = ssl_keyfile
        self.ssl_certfile = ssl_certfile

        assert not (self.use_ssl and self.use_tls), \
            '`use_tls` and `use_ssl` are mutually exclusive, \
only one can be true'

        self.connection = None
        self._lock = threading.RLock()

    def open(self):
        """Open a connection to the email server"""

        # Check if we already have a connection
        if self.connection:
            return

        # Build connection args
        connection_options = {'local_hostname': socket.getfqdn()}
        if self.timeout is not None:
            connection_options['timeout'] = self.timeout

        if self.use_ssl:
            connection_options['keyfile'] = self.ssl_keyfile
            connection_options['certfile'] = self.ssl_certfile

        try:
            # Attempt to connect to the email server
            connection_cls =  smtplib.SMTP
            if self.use_ssl:
                connection_cls = smtplib.SMTP_SSL

            self.connection = connection_cls(
                self.host,
                self.port,
                **connection_options
                )

            # Authentication
            if self.use_tls:

                # Check for a key file and certificate
                tls_args = {}
                if self.ssl_keyfile:
                    tls_args['keyfile'] = self.ssl_keyfile
                if self.ssl_certfile:
                    tls_args['certfile'] = self.ssl_certfile

                self.connection.starttls(**tls_args)

            if self.username and self.password:
                self.connection.login(self.username, self.password)

        except (smtplib.SMTPException, socket.error):
            self.connection = None

            if not self.fail_silently:
                raise

    def close(self):
        """Close the connection the email server"""

        # Check if we have a connection to close
        if self.connection is None:
            return

        # Attempt to close the connection
        try:
            try:
                self.connection.quit()
            except (ssl.SSLError, smtplib.SMTPServerDisconnected):
                self.connection.close()
            except smtplib.SMTPException:
                if not self.fail_silently:
                    raise
        finally:
            self.connection = None

    def send(self, messages):
        """Send all email messages via SMTP"""
        if isinstance(messages, EmailTemplate):
            messages = messages.merge()

        message_count = 0

        with self._lock:
            self.open()

            # Check we have a connection to send with
            if not self.connection:
                return

            for message in messages:
                # Attempt to send the message
                try:
                    self.connection.sendmail(
                        str(message.sender),
                        [str(r) for r in message.recipients],
                        message.message.as_bytes()
                        )
                    message_count += 1
                except smtplib.SMTPException:
                    if not self.fail_silently:
                        raise

            self.close()

        return message_count
