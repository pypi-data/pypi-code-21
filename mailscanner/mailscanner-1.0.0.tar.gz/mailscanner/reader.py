#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import imaplib
import configparser
import os
import email
import email.parser
from email.header import decode_header
from pprint import pprint


class ImapReader:

    def __init__(self, configs):
        self.configs = configs

    def open_connection(self, verbose=False):

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


    # Param: email.message.Message object
    # Returns: string containing the message body
    def get_body(self, msg):
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))

                # skip any text/plain (txt) attachments
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    body = part.get_payload(decode=True)  # decode
                    break

        # not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            body = msg.get_payload(decode=True)
        return body.decode('UTF-8')


    # Extracts subject line from Message object
    def get_subject(self, msg):
        text, encoding = decode_header(msg['subject'])[-1]
        # Text might be encoded, try to decode
        try:
            text = text.decode('UTF-8')
        # If it's already decoded, pass
        except AttributeError:
            pass
        return text


    """
        Params:
            conn        IMAP4_SSL connection
            directory   The IMAP directory to look for
            readonly    readonly mode, true or false
        Returns:
            List of subject-body tuples
    """
    def fetch_all_messages(self, conn, directory, readonly):

        # Selected given directory from given connection
        conn.select(directory, readonly)

        # Initialize an empty list to hold the tuples
        message_data = []

        # Search all messages
        typ, data = conn.search(None, 'All')

        # Loop through each message object
        for num in data[0].split():

            # Fetch message data
            typ, data = conn.fetch(num, '(RFC822)')

            # Go through response parts in the messsage data
            for response_part in data:

                # When a tuple is hit, parse the subject and body
                if isinstance(response_part, tuple):

                    # Read the message using emailparser
                    email_parser = email.parser.BytesFeedParser()
                    email_parser.feed(response_part[1])
                    msg = email_parser.close()

                    # Extract body and subject
                    body = self.get_body(msg)
                    subject = self.get_subject(msg)

                    # Add the data to the list
                    message_data.append((subject, body))

        # Return the list of tuples
        return message_data
