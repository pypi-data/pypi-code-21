from __future__ import absolute_import, division, print_function, unicode_literals

import re

from amaascore.error_messages import ERROR_LOOKUP
from amaascore.core.amaas_model import AMaaSModel


class Address(AMaaSModel):

    def __init__(self, line_one, city, country_id, address_primary, line_two=None, region=None, postal_code=None,
                 *args, **kwargs):
        self.address_primary = address_primary
        self.line_one = line_one
        self.line_two = line_two
        self.city = city
        self.region = region
        self.postal_code = postal_code
        self.country_id = country_id
        super(Address, self).__init__(*args, **kwargs)

    @property
    def country_id(self):
        if hasattr(self, '_country_id'):
            return self._country_id

    @country_id.setter
    def country_id(self, country_id):
        if country_id:
            if len(country_id) != 3:
                raise ValueError(ERROR_LOOKUP.get('country_id_invalid') % country_id)
            self._country_id = country_id


class Email(AMaaSModel):

    def __init__(self, email, email_primary, *args, **kwargs):
        self.email_primary = email_primary
        self.email = email
        super(Email, self).__init__(*args, **kwargs)

    @property
    def email(self):
        if hasattr(self, '_email'):
            return self._email

    @email.setter
    def email(self, email):
        # Validate email addresses
        if not re.match('[^@]+@[^@]+\.[^@]+', email):
            raise ValueError(ERROR_LOOKUP.get('email_address_invalid') % email)
        self._email = email


class Link(AMaaSModel):

    def __init__(self, linked_party_id, *args, **kwargs):
        self.linked_party_id = linked_party_id
        super(Link, self).__init__(*args, **kwargs)
