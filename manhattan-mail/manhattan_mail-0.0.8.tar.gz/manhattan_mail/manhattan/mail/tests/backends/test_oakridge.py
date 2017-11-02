import pytest

from manhattan.mail.backends import oakridge
try:
    from manhattan.mail.tests.oakridge_settings import settings
except:
    settings = {}

# Fixtures

@pytest.fixture(scope='function')
def mailer():
    mailer = oakridge.Mailer(**settings)
    return mailer


# Tests

def test_init():
    """Initialize an email contact"""
    mailer = oakridge.Mailer(**settings)
    assert isinstance(mailer, oakridge.Mailer)

def test_send_email_template(mailer, email_template):
    """Write an email template to memory (as opposed to actually sending them)"""
    response = mailer.send(email_template)

    assert response.status_code == 200