import os

import pytest

from manhattan.mail import (
    EmailAttachment,
    EmailContact,
    EmailMessage,
    EmailTemplate
    )

__all__ = [
    'email_message',
    'email_message_frozen',
    'email_template',
    'email_template_frozen'
    ]


# Classes

class FrozenEmailMessage(EmailMessage):

    def __init__(self, email_message):
        self._message = email_message.message
        self.encoding = email_message.encoding

    @property
    def message(self):
        return self._message


class FrozenEmailTemplate(EmailTemplate):

    def __init__(self, email_template):
        self.email_messages = [
            FrozenEmailMessage(e) for e in email_template.merge()]

    def merge(self):
        return self.email_messages


# Fixtures

@pytest.fixture(scope='function')
def email_message():
    """Return an email message"""
    path = os.path.join(os.path.dirname(__file__), 'data/edison.jpg')
    message = EmailMessage(
        ['burt@example.com'],
        'fred@example.com',
        'Hey',
        body_html='<html><body><p>Hello world</p></body></html>',
        cc=['jojo@example.com'],
        attachments=[EmailAttachment.from_file(path)],
        headers={'Custom-header': 'custom-value'}
        )
    return message

@pytest.fixture(scope='function')
def email_message_frozen(email_message):
    """Return a frozen email message"""
    return FrozenEmailMessage(email_message)

@pytest.fixture(scope='function')
def email_template():
    """Return an email template"""
    path = os.path.join(os.path.dirname(__file__), 'data/edison.jpg')

    template_path = os.path.join(os.path.dirname(__file__), 'data')
    template_map = {}
    for template_name in ['example', 'example_include']:
        with open(os.path.join(template_path, template_name + '.html')) as f:
            template_map[template_name] = f.read()

    template = EmailTemplate(
        ['burt@example.com', 'appa@example.com'],
        'fred@example.com',
        'Hey {{ name }}',
        'example',
        template_map=template_map,
        css='h1 { color: #f00; }',
        recipient_vars={
            'burt@example.com': {'name': 'Burt'},
            'appa@example.com': {'name': 'Appa'},
        },
        global_vars={'company': 'Getme'},
        cc=['jojo@example.com'],
        bcc=['shhh@example.com'],
        attachments=[EmailAttachment.from_file(path)],
        headers={'Custom-header': 'custom-value'}
        )

    return template

@pytest.fixture(scope='function')
def email_template_frozen(email_template):
    """Return an frozen email template"""
    return FrozenEmailTemplate(email_template)
