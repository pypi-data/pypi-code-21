from io import StringIO
import pytest

from manhattan.mail.backends import console


# Fixtures

@pytest.fixture(scope='function')
def mailer():
    stream = StringIO()
    mailer = console.Mailer(stream)
    mailer.stream = stream
    return mailer


# Utils

def write_message(message):
    stream = StringIO()
    msg_data = message.message.as_bytes()
    msg_data = msg_data.decode(message.encoding)
    stream.write('%s\n' % msg_data)
    stream.write('-' * 79)
    stream.write('\n')
    return stream.getvalue()

# Tests

def test_init():
    """Initialize an email contact"""
    mailer = console.Mailer()
    assert isinstance(mailer, console.Mailer)

def test_send_email_message(mailer, email_message_frozen):
    """Write an email message to memory (as opposed to actually sending them)"""
    mailer.send([email_message_frozen])
    assert mailer.stream.getvalue() == write_message(email_message_frozen)

def test_send_email_template(mailer, email_template_frozen):
    """Write an email template to memory (as opposed to actually sending them)"""
    email_messages = email_template_frozen.merge()
    mailer.send(email_template_frozen)

    output = write_message(email_messages[0])
    output += write_message(email_messages[1])
    mailer.stream.getvalue() == output
