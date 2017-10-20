# Copyright (C) 2017 Pier Carlo Chiodi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from email.mime.text import MIMEText
import logging.handlers
import smtplib


class BufferedSMTPHandler(logging.handlers.BufferingHandler):

    def __init__(self, mailhost, fromaddr, toaddrs, subject,
                 credentials=None, secure=None, timeout=None,
                 capacity=100):
        logging.handlers.BufferingHandler.__init__(self, capacity)

        assert isinstance(toaddrs, list), \
            "toaddrs must be a list of strings"
        assert all(isinstance(_, str) for _ in toaddrs), \
            "toaddrs must be a list of strings"
        self.toaddrs = toaddrs

        assert isinstance(mailhost, (tuple, str)), \
            "mailhost must be a string or a tuple (host, port)"

        if isinstance(mailhost, tuple):
            assert len(mailhost) == 2, \
                "mailhost must be a tuple of 2 elements (host, port)"
            assert isinstance(mailhost[0], str), \
                "the first element of mailhost must be a string"
            assert isinstance(mailhost[1], int), \
                "the second element of mailhost must be an int"

            self.mailhost = mailhost[0]
            self.mailport = mailhost[1]
        else:
            self.mailhost = mailhost
            self.mailport = None

        if credentials is not None:
            assert isinstance(credentials, tuple), \
                "credentials must be a tuple (username, password)"
            assert len(credentials) == 2, \
                "credentials must be a tuple of two elements (user, pass)"

            self.smtp_username = credentials[0]
            self.smtp_password = credentials[1]
        else:
            self.smtp_username = None
            self.smtp_password = None

        if secure is not None:
            assert isinstance(secure, tuple) and len(secure) <= 2, \
                ("secure must be an empty tuple, or a single-value tuple "
                 "with the name of a keyfile, or a 2-value tuple with the "
                 "names of the keyfile and certificate file")
        self.secure = secure

        self.timeout = timeout

        assert isinstance(fromaddr, str), \
            "fromaddr must be a string"
        self.fromaddr = fromaddr

        assert isinstance(subject, str), \
            "subject must be a string"
        self.subject = subject

    def create_smtp(self):
        return smtplib.SMTP(self.mailhost, self.mailport, None, self.timeout)

    def starttls(self, smtp):
        if self.secure:
            smtp.starttls(*self.secure)
            smtp.ehlo()

    def flush(self):
        if len(self.buffer) == 0:
            return

        try:
            smtp = self.create_smtp()

            if self.smtp_username and self.smtp_password:
                smtp.login(self.smtp_username, self.smtp_password)

            self.starttls(smtp)

            body = ""
            for record in self.buffer:
                s = self.format(record)
                body += s + "\r\n"

            msg = MIMEText(body)
            msg["Subject"] = self.subject
            msg["From"] = self.fromaddr
            msg["To"] = ", ".join(self.toaddrs)

            smtp.sendmail(self.fromaddr, self.toaddrs, msg.as_string())
            smtp.quit()
        except Exception:
            self.handleError(None)  # no particular record

        self.buffer = []


class BufferedSMTPHandlerSSL(BufferedSMTPHandler):

    def create_smtp(self):
        key_file = None
        cert_file = None
        if self.secure:
            if len(self.secure) >= 1:
                key_file = self.secure[0]
            if len(self.secure) == 2:
                cert_file = self.secure[1]

        return smtplib.SMTP_SSL(self.mailhost, self.mailport, None,
                                key_file, cert_file, self.timeout)

    def starttls(self, smtp):
        return
