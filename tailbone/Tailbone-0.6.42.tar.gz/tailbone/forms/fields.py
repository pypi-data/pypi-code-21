# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
FormAlchemy Fields
"""

from __future__ import unicode_literals, absolute_import

import formalchemy as fa


def AssociationProxyField(name, **kwargs):
    """
    Returns a FormAlchemy ``Field`` class which is aware of association
    proxies.
    """

    class ProxyField(fa.Field):

        def sync(self):
            if not self.is_readonly():
                setattr(self.parent.model, self.name,
                        self.renderer.deserialize())

    def value(obj):
        return getattr(obj, name, None)

    kwargs.setdefault('value', value)
    return ProxyField(name, **kwargs)


class DefaultEmailField(fa.Field):
    """
    Generic field for view/edit of default email address for a contact
    """

    def __init__(self, name=None, **kwargs):
        kwargs.setdefault('value', self.value)
        if 'renderer' not in kwargs:
            from tailbone.forms.renderers import EmailFieldRenderer
            kwargs['renderer'] = EmailFieldRenderer
        super(DefaultEmailField, self).__init__(name, **kwargs)

    def value(self, contact):
        if contact.emails:
            return contact.emails[0].address

    def sync(self):
        if not self.is_readonly():
            address = self._deserialize()
            contact = self.parent.model
            if contact.emails:
                if address:
                    email = contact.emails[0]
                    email.address = address
                else:
                    contact.emails.pop(0)
            elif address:
                email = contact.add_email_address(address)


class DefaultPhoneField(fa.Field):
    """
    Generic field for view/edit of default phone number for a contact
    """

    def __init__(self, name=None, **kwargs):
        kwargs.setdefault('value', self.value)
        super(DefaultPhoneField, self).__init__(name, **kwargs)

    def value(self, contact):
        if contact.phones:
            return contact.phones[0].number

    def sync(self):
        if not self.is_readonly():
            number = self._deserialize()
            contact = self.parent.model
            if contact.phones:
                if number:
                    phone = contact.phones[0]
                    phone.number = number
                else:
                    contact.phones.pop(0)
            elif number:
                phone = contact.add_phone_number(number)
