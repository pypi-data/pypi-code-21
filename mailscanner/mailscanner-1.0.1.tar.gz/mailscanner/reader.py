#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import imaplib
import email
import email.parser
from email.header import decode_header


class ImapReader:
    """ Opens a connection to IMAP server and fetces all messages."""

    def __init__(self, configs):
        self.configs = configs

    def open_connection(self, verbose=False):
        """ Initializes a new IMAP4_SSL connection to an email server."""

        # Connect to server
        hostname = self.configs.get('IMAP', 'hostname')
        if verbose:
            print('Connecting to ' + hostname)
        connection = imaplib.IMAP4_SSL(hostname)

        # Authenticate
        username = self.configs.get('IMAP', 'username')
        password = self.configs.get('IMAP', 'password')
        if verbose:
            print('Logging in as', username)
        connection.login(username, password)

        return connection


    def get_body(self, msg):
        """ Extracts and returns the decoded body from an EmailMessage object"""

        body = ""
        charset = ""

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))

                # skip any text/plain (txt) attachments
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    body = part.get_payload(decode=True)  # decode
                    charset = part.get_content_charset()
                    break

        # not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            body = msg.get_payload(decode=True)
            charset = msg.get_content_charset()

        return body.decode(charset)


    def get_subject(self, msg):
        """Extracts the subject line from an EmailMessage object."""

        text, encoding = decode_header(msg['subject'])[-1]

        try:
            text = text.decode(encoding)

        # If it's already decoded, ignore error
        except AttributeError:
            pass

        return text


    def fetch_all_messages(self, conn, directory, readonly):
        """ Fetches all messages at @conn from @directory.

            Params:
                conn        IMAP4_SSL connection
                directory   The IMAP directory to look for
                readonly    readonly mode, true or false
            Returns:
                List of subject-body tuples
        """

        conn.select(directory, readonly)

        message_data = []

        typ, data = conn.search(None, 'All')

        # Loop through each message object
        for num in data[0].split():

            typ, data = conn.fetch(num, '(RFC822)')

            for response_part in data:

                if isinstance(response_part, tuple):

                    email_parser = email.parser.BytesFeedParser()
                    email_parser.feed(response_part[1])

                    msg = email_parser.close()

                    body = self.get_body(msg)
                    subject = self.get_subject(msg)

                    message_data.append((subject, body))

        return message_data
