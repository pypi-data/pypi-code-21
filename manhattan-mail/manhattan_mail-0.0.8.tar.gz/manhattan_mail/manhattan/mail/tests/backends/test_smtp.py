import os
import pytest


from manhattan.mail import (
    EmailAttachment,
    EmailMessage
    )
from manhattan.mail.backends import smtp
try:
    from manhattan.mail.tests.smtp_settings import settings
except:
    settings = {}

# Fixtures

@pytest.fixture(scope='function')
def mailer():
    mailer = smtp.Mailer(**settings)
    return mailer


# Tests

def test_init():
    """Initialize an email contact"""
    mailer = smtp.Mailer(**settings)
    assert isinstance(mailer, smtp.Mailer)

def test_send_email_message(mailer):
    """Write an email message to memory (as opposed to actually sending them)"""
    if not settings:
        return

    path = os.path.join(os.path.dirname(__file__), '../data/edison.jpg')
    email_message = EmailMessage(
        ['ant@getme.co.uk'],
        'devs@getme.co.uk',
        'Hey',
        body_html='<html><body><p>Hello world</p></body></html>',
        attachments=[EmailAttachment.from_file(path)],
        headers={'Custom-header': 'custom-value'}
        )
    mailer.send([email_message])

    assert True
