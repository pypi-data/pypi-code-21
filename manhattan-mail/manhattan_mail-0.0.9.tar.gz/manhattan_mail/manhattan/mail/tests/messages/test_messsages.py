from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

from manhattan.mail import EmailAttachment, EmailContact, EmailMessage


def test_init():
    """Initialize an email message"""
    message = EmailMessage(
        ['burt@example.com'],
        'fred@example.com',
        'Hey',
        body_text='Hello world'
        )
    assert isinstance(message, EmailMessage)

def test_auto_text():
    """Generate a text alternative if no text body is provided"""
    message = EmailMessage(
        'burt@example.com',
        'fred@example.com',
        'Hey',
        body_html='<html><body><p>Hello world</p></body></html>'
        )
    assert message.body_text == 'Hello world\n\n'

def test_attach():
    """Attach a file to the email message"""
    message = EmailMessage(
        ['burt@example.com'],
        'fred@example.com',
        'Hey',
        body_text='Hello world'
        )
    path = os.path.join(os.path.dirname(__file__), '../data/edison.jpg')
    attachment = message.attach(path)

    assert len(message.attachments) == 1
    assert message.attachments[-1] == attachment

def test_message():
    """Return an email message"""
    path = os.path.join(os.path.dirname(__file__), '../data/edison.jpg')
    message = EmailMessage(
        ['burt@example.com'],
        'fred@example.com',
        'Hey',
        body_html='<html><body><p>Hello world</p></body></html>',
        cc=['jojo@example.com'],
        attachments=[EmailAttachment.from_file(path)],
        headers={'Custom-header': 'custom-value'}
        )
    msg = message.message
    payload =  msg.get_payload()

    assert isinstance(msg, MIMEMultipart)
    assert msg['Subject'] == message.subject
    assert msg['From'] == str(message.sender)
    assert msg['To'] == ', '.join([str(t) for t in message.to])
    assert msg['Cc'] == ', '.join([str(c) for c in message.cc])

    assert len(payload) == 2
    assert payload[0].get_payload()[0].get_payload() == 'Hello world\n\n'
    assert payload[0].get_payload()[1].get_payload() == \
            '<html><body><p>Hello world</p></body></html>'
    assert isinstance(payload[1], MIMEImage)

def test_recipients():
    """Return a list of all recipients for an email message (to, cc, bcc)"""
    message = EmailMessage(
        ['burt@example.com'],
        'fred@example.com',
        'Hey',
        body_text='Hello world',
        cc=['jojo@example.com'],
        bcc=['appa@example.com']
        )

    assert message.recipients == EmailContact.normalize([
        'burt@example.com',
        'jojo@example.com',
        'appa@example.com'
        ])
