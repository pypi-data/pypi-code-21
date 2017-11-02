from io import StringIO
import os
import pytest

from manhattan.mail.backends import file


# Fixtures

@pytest.fixture(scope='function')
def mailer():
    mailer = file.Mailer(os.path.join(os.getcwd(), 'test-output/test.eml'))
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
    mailer = file.Mailer('some_file_path.eml')
    assert isinstance(mailer, file.Mailer)

def test_send_email_message(mailer, email_message_frozen):
    """Write an email message to file (as opposed to actually sending them)"""
    mailer.send([email_message_frozen])
    with open(mailer.file_path) as f:
        assert f.read() == write_message(email_message_frozen)

def test_send_email_template(mailer, email_template_frozen):
    """Write an email template to file (as opposed to actually sending them)"""
    email_messages = email_template_frozen.merge()
    mailer.send(email_template_frozen)

    output = write_message(email_messages[0])
    output = write_message(email_messages[1])

    with open(mailer.file_path) as f:
        assert f.read() == output