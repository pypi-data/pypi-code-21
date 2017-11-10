from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.random_utils import random_string
import datetime
import random

from amaascore.monitor.item import Item


def generate_item(client_id=None, asset_manager_id=None, item_id=None, item_class=None, item_type=None,
                  item_level=None, item_source=None, item_date=None, message=None):

    item = Item(
        client_id=client_id or random.randint(1, 2**31-1),
        asset_manager_id=asset_manager_id or random.randint(1, 1000),
        item_id=item_id or random_string(10),
        item_class=item_class or random.choice(['Exception', 'Notification']),
        item_type=item_type or random_string(15),
        item_level=item_level or random.choice(['Info', 'Warning', 'Error', 'Critical']),
        item_source=item_source or random.choice(['Transactions', 'Assets', random_string(20)]),
        item_date=item_date or datetime.date.today(),
        message=message or random_string(200)
    )
    return item


def generate_items(asset_manager_ids=[], number=5):
    items = []
    for i in range(number):
        item = generate_item(asset_manager_id=random.choice(asset_manager_ids))
        items.append(item)
    return items
