#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
import os
import json
import base64
import hashlib
import mailbox
from plant import Node
from bs4 import BeautifulSoup
import email.Header

reload(sys)
sys.setdefaultencoding('utf-8')

node = Node(__file__).dir.parent


def json_default(obj):
    try:
        return list(obj)
    except:
        return repr(obj)


def content_type_is_binary(content_type):
    return (
        'image' in content_type or
        'video' in content_type or
        'application' in content_type or
        'octet-stream' in content_type
    )


def checksum(item):
    return hashlib.sha256(item.encode('utf-8')).hexdigest()


def strip_ltgt(s):
    return re.sub('^[<](.*)[>]$', r'\g<1>', s)


class EmailMessage(object):
    def __init__(self, id_and_msg):
        self.id, self.msg = id_and_msg

    @classmethod
    def from_internet_message_string(cls, string):
        message = mailbox.Message(string)
        return cls((message['Message-ID'], message))

    def extract_relevant_metadata(self, metadata):
        # import ipdb;ipdb.set_trace()
        to_og = metadata.pop('To', None)
        to, toencoding = email.Header.decode_header(to_og)[0]
        # if not to:
        #     return {}

        fallback_from_og = metadata.get('Return-Path',
                                        metadata.get('Reply-To',
                                                     metadata.pop('From', '')))
        # if not fallback_from:
        #     return {}
        fallback_from, fencoding = email.Header.decode_header(fallback_from_og)[0]

        data = {}
        data[b'id'] = checksum(self.msg.as_string())
        data[b'to'] = strip_ltgt(to)
        data[b'to_encoding'] = toencoding
        data[b'from'] = strip_ltgt(fallback_from)
        data[b'from_encoding'] = fencoding
        data[b'priority'] = metadata.pop('X-Priority',
                                         metadata.pop('X-MSMail-Priority', None))
        data[b'importance'] = metadata.pop('Importance', None)
        data[b'received'] = metadata.pop('Received', None)
        data[b'date'] = metadata.pop('Date', None)
        data[b'mailer'] = metadata.pop('X-Mailer', None)
        data[b'mime-version'] = metadata.pop('MIME-Version', None)

        subject, sencoding = email.Header.decode_header(metadata.pop('Subject', ''))[0]
        data[b'subject'] = subject
        data[b'subject_encoding'] = sencoding
        data[b'content-type'] = metadata.pop('Content-Type', None)

        data[b'meta'] = dict([(k.lower(), v) for k, v in metadata.iteritems()])
        return data

    def extract_message(self, message):
        if isinstance(message, basestring):
            return {
                'id': checksum(message),
                'body': message
            }
        preview = None

        all_params = message.get_params()
        ((content_type, _), (_, charset)) = all_params
        body = message.get_payload(decode=True)

        if isinstance(body, mailbox.Message):
            return self.extract_message(body)

        parts = []
        if message.is_multipart():
            for m in message.get_payload():
                part = self.extract_message(m)
                if preview is None and part.get('preview') is not None:
                    preview = part.get('preview')

                parts.append(part)

        if 'text' in content_type:
            body = body.decode(charset)

        elif content_type_is_binary(content_type):
            body = base64.b64encode('base64')

        dom = BeautifulSoup(body, 'html.parser')

        if 'html' in (content_type or '').lower():
            paragraphs = [p.get_text() for p in dom.findAll('p') or dom.findAll('div') or dom.findAll('span')]
            if dom.body:
                body = dom.body.prettify()
                clean_body = dom.body.get_text().strip()
                paragraphs = clean_body.splitlines()
            else:
                body = dom.prettify()
                clean_body = "\n".join(paragraphs)

        elif content_type == 'text/plain':
            clean_body = body.strip()
            paragraphs = clean_body.splitlines()
        else:
            clean_body = body
            paragraphs = []

        if paragraphs:
            preview = paragraphs[0].strip()

        return {
            'preview': preview,
            'is_multipart': self.msg.is_multipart(),
            'content_type': content_type,
            'parts': parts,
            'paragraphs': paragraphs,
            'encoding': charset,
            'body': body,
            'clean_body': clean_body,
            'id': checksum(message.as_string())
        }

    def to_dict(self):
        metadata = dict(self.msg.items())

        data = self.extract_relevant_metadata(metadata)
        data[b'ims'] = self.msg.as_string()
        data[b'parts'] = [self.extract_message(msg) for msg in self.msg.get_payload()]
        return data

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent, default=json_default)


class JSONInBox(object):
    def __init__(self, path, capture_subdomains=None):
        self.capture_subdomains = capture_subdomains or []
        self.path = path
        self.box = []

    def scan(self, filters=None):
        filters = filters or []
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                if not filename.lower().endswith('.json'):
                    continue

                with open(os.path.join(root, filename), 'rb') as fd:
                    data = json.load(fd)
                    email_uuid = data.pop('email_uuid',
                                          data.pop('uuid', None))
                    data['filename'] = filename
                    ims = data['body'].encode('utf-8')
                    data['uuid'] = email_uuid
                    data.update(EmailMessage((email_uuid, mailbox.Message(ims))).to_dict())

                    to = data.get('to', None)
                    if not to:
                        continue

                    if isinstance(to, basestring) and not any([domain in to for domain in self.capture_subdomains]):
                        continue

                    if isinstance(to, (tuple, list)) and not any([domain in x for x in to for domain in self.capture_subdomains]):
                        continue

                    for validate in filter(callable, filters):
                        if not validate(data):
                            continue

                    self.box.append(data)
                    yield data


def main():
    inbox = JSONInBox(node.join('mail'))
    print inbox.path
    emails = inbox.scan()
    for message in emails:
        print message.to_json()

    print "total", len(emails)


if __name__ == '__main__':
    main()
