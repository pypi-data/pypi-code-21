from manhattan.mail import EmailContact


def test_init():
    """Initialize an email contact"""
    contact = EmailContact('burt@example.com', 'Burt')
    assert isinstance(contact, EmailContact)

def test_eq():
    """Compare email contacts for equality"""
    contact_a = EmailContact('burt@example.com', 'Burt')
    contact_b = EmailContact('burt@example.com')
    contact_c = EmailContact('fred@example.com', 'Fred')

    assert contact_a == contact_b
    assert contact_a != contact_c

def test_hash():
    """Return a unique hash value for the contact"""
    contact_a = EmailContact('burt@example.com', 'Burt')
    contact_b = EmailContact('burt@example.com')
    assert hash(contact_a) == hash(contact_b)

def test_str():
    """Convert to an address string"""
    contact = EmailContact('burt@example.com', 'Burt')
    assert str(contact) == 'Burt <burt@example.com>'

def test_tuple():
    """Convert to a tuple"""
    contact = EmailContact('burt@example.com', 'Burt')
    assert tuple(contact) == ('burt@example.com', 'Burt', 'utf-8')

def test_normalize():
    """
    Convert a list of email address of the form string, tuple or `EmailContact`
    to a list of `EmailContact` instances.
    """
    contacts = EmailContact.normalize([
        'jojo@example.com',
        ('burt@example.com', 'Burt'),
        EmailContact('fred@example.com', 'Fred')
        ])

    assert len(contacts) == 3
    for contact in contacts:
        assert isinstance(contact, EmailContact)
