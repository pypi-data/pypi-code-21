import pytest

from manhattan.mail.backends import memory


# Fixtures

@pytest.fixture(scope='function')
def mailer():
    mailer = memory.Mailer()
    mailer.clear()
    return mailer


# Tests

def test_init():
    """Initialize an email contact"""
    mailer = memory.Mailer()
    assert isinstance(mailer, memory.Mailer)

def test_clear(mailer, email_message):
    """Clear the outbox"""
    assert len(mailer.outbox) == 0

    mailer.send([email_message])
    assert len(mailer.outbox) == 1

    mailer.clear()
    assert len(mailer.outbox) == 0

def test_send_email_message(mailer, email_message):
    """Write an email message to memory (as opposed to actually sending them)"""
    mailer.send([email_message])

    assert len(mailer.outbox) == 1
    mailer.outbox[0] == email_message

def test_send_email_template(mailer, email_template):
    """Write an email template to memory (as opposed to actually sending them)"""
    email_messages = email_template.merge()

    mailer.send(email_template)

    assert len(mailer.outbox) == 2
    mailer.outbox[0] == email_messages[0]
    mailer.outbox[1] == email_messages[1]
