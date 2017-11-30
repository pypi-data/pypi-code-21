from __future__ import absolute_import, division, print_function, unicode_literals

import copy

from amaascore.error_messages import ERROR_LOOKUP
from amaascore.core.amaas_model import AMaaSModel
from amaascore.core.comment import Comment
from amaascore.core.reference import Reference
from amaascore.parties.children import Address, Email, Link
from amaascore.parties.enums import PARTY_STATUSES


class Party(AMaaSModel):

    @staticmethod
    def children():
        """ A dict of which of the attributes are collections of other objects, and what type """
        return {'addresses': Address, 'comments': Comment, 'emails': Email, 'links': Link, 'references': Reference}

    def __init__(self, asset_manager_id, party_id, party_status='Active', base_currency=None, display_name='', legal_name='', url='', description='',
                 addresses=None, comments=None, emails=None, links=None, references=None, *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.party_id = party_id
        self.party_status = party_status
        if not hasattr(self, 'party_class'):  # A more specific child class may have already set this
            self.party_class = 'Party'
        self.party_type = self.__class__.__name__
        self.base_currency = base_currency
        self.display_name = display_name
        self.legal_name = legal_name
        self.url = url
        self.description = description
        # Defaults are here not in constructor for mutability reasons.
        self.addresses = addresses.copy() if addresses else {}
        self.comments = comments.copy() if comments else {}
        self.emails = emails.copy() if emails else {}
        self.links = links.copy() if links else {}
        self.references = references.copy() if references else {}
        super(Party, self).__init__(*args, **kwargs)

    def upsert_address(self, address_type, address):
        addresses = copy.deepcopy(self.addresses)
        addresses.update({address_type: address})
        self.addresses = addresses

    @property
    def addresses(self):
        if hasattr(self, '_addresses'):
            return self._addresses

    @addresses.setter
    def addresses(self, addresses):
        if not isinstance(addresses, dict):
            raise ValueError(ERROR_LOOKUP.get('address_invalid') % (str(addresses), self.party_id,
                                                                    self.asset_manager_id))
        primary = [address.address_primary for address in addresses.values() if address.address_primary]
        # If addresses are present, one of them must be primary
        if len(addresses) and len(primary) != 1:
            raise ValueError(ERROR_LOOKUP.get('address_primary') % (self.party_id, self.asset_manager_id))
        self._addresses = addresses

    def upsert_email(self, email_type, email):
        emails = copy.deepcopy(self.emails)
        emails.update({email_type: email})
        self.emails = emails

    @property
    def emails(self):
        if hasattr(self, '_emails'):
            return self._emails

    @emails.setter
    def emails(self, emails):
        if not isinstance(emails, dict):
            raise ValueError(ERROR_LOOKUP.get('email_invalid') % (str(emails), self.party_id, self.asset_manager_id))
        primary = [email.email_primary for email in emails.values() if email.email_primary]
        # If emails are present, one of them must be primary
        if len(emails) and len(primary) != 1:
            raise ValueError(ERROR_LOOKUP.get('email_primary') % (self.party_id, self.asset_manager_id))
        self._emails = emails

    @property
    def party_status(self):
        if hasattr(self, '_party_status'):
            return self._party_status

    @party_status.setter
    def party_status(self, party_status):
        """

        :param transaction_status: The status of the transaction - e.g. Active, Inactive
        :return:
        """
        if party_status not in PARTY_STATUSES:
            raise ValueError(ERROR_LOOKUP.get('party_status_invalid') % (party_status, self.party_id,
                                                                         self.asset_manager_id))
        else:
            self._party_status = party_status
