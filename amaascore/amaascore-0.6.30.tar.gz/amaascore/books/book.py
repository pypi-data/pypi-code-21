from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import uuid
import pytz

from amaascore.error_messages import ERROR_LOOKUP
from amaascore.books.enums import BOOK_TYPES
from amaascore.core.amaas_model import AMaaSModel


class Book(AMaaSModel):

    @staticmethod
    def non_interface_attributes():
        return ['positions']

    def __init__(self, asset_manager_id, book_id=None, book_type='Trading', book_status='Active', owner_id=None,
                 party_id=None, close_time=None, timezone='', base_currency='USD',
                 business_unit='', reference='', description='', positions=None,
                 *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.book_id = book_id or uuid.uuid4().hex
        self.book_type = book_type
        self.book_status = book_status
        self.owner_id = owner_id or party_id  # This could still be None if neither are set, which will raise an error
        self.party_id = party_id
        self.close_time = close_time
        self.timezone = timezone
        self.base_currency = base_currency
        self.business_unit = business_unit
        self.reference = reference
        self.description = description
        self.positions = positions
        super(Book, self).__init__(*args, **kwargs)

    def positions_by_asset(self):
        """
        A dictionary of Position objects keyed by asset_id.
        :return:
        """
        return {position.asset_id: position for position in self.positions}

    @property
    def book_type(self):
        if hasattr(self, '_book_type'):
            return self._book_type

    @book_type.setter
    def book_type(self, book_type):
        """

        :param book_type: The type of book that we are creating - e.g. Trading, Wash
        :return:
        """
        if book_type not in BOOK_TYPES:
            raise ValueError(ERROR_LOOKUP.get('book_type_invalid') % (book_type, self.book_id, self.asset_manager_id))
        else:
            self._book_type = book_type

    def utc_book_close_time(self):
        """
        The book close time in utc.
        """
        tz = pytz.timezone(self.timezone)
        close_time = datetime.datetime.strptime(self.close_time, '%H:%M:%S').time()
        close_time = tz.localize(datetime.datetime.combine(datetime.datetime.now(tz), close_time))
        return close_time.astimezone(pytz.utc).time()
