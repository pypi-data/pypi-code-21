from __future__ import absolute_import, division, print_function, unicode_literals

from dateutil.parser import parse
import sys
import uuid

from amaascore.core.amaas_model import AMaaSModel

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Item(AMaaSModel):

    def __init__(self, asset_manager_id, item_class, item_type, item_level, item_source, message, item_id=None,
                 item_status='Open', asset_book_id=None, transaction_id=None, asset_id=None, item_date=None,
                 *args, **kwargs):

        self.asset_manager_id = asset_manager_id
        self.item_id = item_id or uuid.uuid4().hex
        self.item_class = item_class
        self.item_type = item_type
        self.item_level = item_level
        self.item_source = item_source
        self.message = message
        self.item_status = item_status
        self.asset_book_id = asset_book_id
        self.transaction_id = transaction_id
        self.asset_id = asset_id
        self.item_date = item_date
        super(Item, self).__init__(*args, **kwargs)

    @property
    def item_date(self):
        if hasattr(self, '_item_date'):
            return self._item_date

    @item_date.setter
    def item_date(self, item_date):
        """

        :param item_date:
        :return:
        """
        if item_date:
            self._item_date = parse(item_date).date() if isinstance(item_date, type_check) else item_date
