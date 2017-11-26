from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.monitor.item import Item


def json_to_item(json_item):
    item = Item(**json_item)
    return item
