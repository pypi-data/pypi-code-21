from email.mime.text import MIMEText
import os

from manhattan.mail import EmailAttachment


def test_init():
    """Initialize an email attachment"""
    attachment = EmailAttachment('hello-world.txt', 'Hello world')
    assert isinstance(attachment, EmailAttachment)

def test_attachment():
    """Return an attachment message"""
    attachment = EmailAttachment('hello-world.txt', 'Hello world').attachment

    assert isinstance(attachment, MIMEText)
    assert attachment.get_payload() == 'Hello world'
    assert attachment['Content-Disposition'] == \
            'attachment; filename="hello-world.txt"'

def test_from_file():
    """Create an attachment from a file"""

    # File path
    path = os.path.join(os.path.dirname(__file__), '../data/edison.jpg')
    attachment = EmailAttachment.from_file(path)

    assert isinstance(attachment, EmailAttachment)
    assert attachment.filename == 'edison.jpg'
    assert attachment.mimetype == 'image/jpeg'

    # File object
    with open(path, 'rb') as f:
        attachment = EmailAttachment.from_file(f)

        assert isinstance(attachment, EmailAttachment)
        assert attachment.filename == 'edison.jpg'
        assert attachment.mimetype == 'image/jpeg'
