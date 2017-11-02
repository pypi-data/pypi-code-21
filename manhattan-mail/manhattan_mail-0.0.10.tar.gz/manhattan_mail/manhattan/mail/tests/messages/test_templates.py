from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

from jinja2 import Environment, FileSystemLoader

from manhattan.mail import (
    EmailAttachment,
    EmailContact,
    EmailMessage,
    EmailTemplate
    )



class CustomEmailTemplate(EmailTemplate):
    """
    An `EmailTemplate` class set up for the test environment.
    """

    def get_jinja_env(self):
        path = os.path.join(os.path.dirname(__file__), '../data/')
        return Environment(
            loader=FileSystemLoader(path),
            autoescape=True
            )


# Tests

def test_init():
    """Initialize an email template"""
    template = EmailTemplate(
        ['burt@example.com'],
        'fred@example.com',
        'Hey {{ name }}',
        'example.html'
        )
    assert isinstance(template, EmailTemplate)

def test_attach():
    """Attach a file to the email message"""
    message = EmailTemplate(
        ['burt@example.com'],
        'fred@example.com',
        'Hey {{ name }}',
        'example.html'
        )
    path = os.path.join(os.path.dirname(__file__), '../data/edison.jpg')
    attachment = message.attach(path)

    assert len(message.attachments) == 1
    assert message.attachments[-1] == attachment

def test_merge_template_file():
    """Mail merge using a template file to create list of email messages"""
    path = os.path.join(os.path.dirname(__file__), '../data/edison.jpg')
    template = CustomEmailTemplate(
        ['burt@example.com', 'appa@example.com'],
        'fred@example.com',
        'Hey {{ name }}',
        'example.html',
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
    messages = template.merge()

    assert len(messages) == 2
    assert messages[0].body_html == '''<html>
    <head><style type="text/css">h1 { color: #f00; }</style></head>
<body>
        <h1 style="color:#f00">Getme</h1>
        <p>Burt</p>
        <p>Footer</p>
    </body>
</html>
'''
    assert len(messages[0].attachments) == 1

    assert messages[1].body_html == '''<html>
    <head><style type="text/css">h1 { color: #f00; }</style></head>
<body>
        <h1 style="color:#f00">Getme</h1>
        <p>Appa</p>
        <p>Footer</p>
    </body>
</html>
'''
    assert len(messages[1].attachments) == 1

def test_merge_template_map():
    """Mail merge using a template file to create list of email messages"""
    path = os.path.join(os.path.dirname(__file__), '../data/edison.jpg')

    template_path = os.path.join(os.path.dirname(__file__), '../data')
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
    messages = template.merge()

    assert len(messages) == 2
    assert messages[0].body_html == '''<html>
    <head><style type="text/css">h1 { color: #f00; }</style></head>
<body>
        <h1 style="color:#f00">Getme</h1>
        <p>Burt</p>
        <p>Footer</p>
    </body>
</html>
'''
    assert len(messages[0].attachments) == 1

    assert messages[1].body_html == '''<html>
    <head><style type="text/css">h1 { color: #f00; }</style></head>
<body>
        <h1 style="color:#f00">Getme</h1>
        <p>Appa</p>
        <p>Footer</p>
    </body>
</html>
'''
    assert len(messages[1].attachments) == 1
