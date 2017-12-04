import csv
from datetime import date, datetime
from dateutil.parser import parse
from decimal import Decimal
from amaasutils.csv_upload_utils import *

from amaascore.tools.csv_tools import csv_stream_to_objects
from amaasutils.logging_utils import DEFAULT_LOGGING

from amaascore.assets.interface import AssetsInterface
from amaascore.parties.interface import PartiesInterface
from amaascore.books.interface import BooksInterface
from amaascore.corporate_actions.interface import CorporateActionsInterface
from amaascore.market_data.interface import MarketDataInterface
from amaascore.transactions.interface import TransactionsInterface
from amaascore.asset_managers.interface import AssetManagersInterface

from amaascore import parties
from amaascore import assets
from amaascore import transactions

from amaascore.assets.children import Link, Reference
from amaascore.parties.children import Address, Email, Link, Reference, Comment
from amaascore.transactions.children import Charge, Code, Comment, Link, Party, Rate, Reference

CHILDREN_CLASS = {'asset': {'links': assets.children.Link, 'references': assets.children.Reference},
                  'party': {'addresses': parties.children.Address, 'emails': parties.children.Email,
                            'links': parties.children.Link, 'references': parties.children.Reference,
                            'comments': parties.children.Comment},
                  'transaction': {'charges': transactions.children.Charge, 'codes': transactions.children.Code,
                                  'comments': transactions.children.Comment, 'links': transactions.children.Link,
                                  'rates': transactions.children.Rate, 'parties': transactions.children.Party,
                                  'references': transactions.children.Reference},
                  'asset_manager': {},
                  'book': {},
                  'corporate_action': {'references': assets.children.Reference}} #no Reference class found in corporate_actions

def direct_to_class(amaasclass):
    """direct from amaasclass (first params given in the row) to the dictionary of the children class"""
    if amaasclass in ASSET:
        return CHILDREN_CLASS['asset']
    elif amaasclass in PARTY:
        return CHILDREN_CLASS['party']
    elif amaasclass in TRANSACTION:
        return CHILDREN_CLASS['transaction']
    elif amaasclass in BOOK:
        return CHILDREN_CLASS['book']
    elif amaasclass in CORPORATE_ACTION:
        return CHILDREN_CLASS['corporate_action']
    elif amaasclass in MARKET_DATA:
        return None #None for now
    else:
        return CHILDREN_CLASS['asset_manager']

def interface_direct_class(data_class):
    """help to direct to the correct interface interacting with DB by class name only"""
    if data_class in ASSET:
        interface = AssetsInterface()
    elif data_class in PARTY:
        interface = PartiesInterface()
    elif data_class in BOOK:
        interface = BooksInterface()
    elif data_class in CORPORATE_ACTION:
        interface = CorporateActionsInterface()
    elif data_class in MARKET_DATA:
        interface = MarketDataInterface()
    elif data_class in TRANSACTION:
        interface = TransactionsInterface()
    else:
        interface = AssetManagersInterface()
    return interface

def interface_direct_csvpath(csvpath):
    """help to direct to the correct interface interacting with DB by csvfile path"""
    with open(csvpath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_class = row.pop('amaasclass', '')
            return interface_direct_class(data_class)

def process_normal(_dict):
    """
    this method process the _dict to correct dict to be called by class constructor
    this method will be imported and called by main csv uploader function
    """
    cooked_dict = group_raw_to_formatted_string_dict(_dict)
    data_class = cooked_dict.pop('amaasclass', '')
    children_class_dict = direct_to_class(data_class)
    tasty_dict = dict()
    for cooked_key, cooked_value in cooked_dict.items():
        if cooked_key in CHILDREN_SIGNAL:
            processed_dict = {cooked_key: formatted_string_to_others(cooked_value, children_class_dict[cooked_key])}
        elif cooked_key == 'links':
            processed_dict = {cooked_key: formatted_string_to_links(cooked_value, children_class_dict[cooked_key])}
        else:
            processed_dict = {cooked_key: process_value_with_header(cooked_key, cooked_value)}
        tasty_dict.update(processed_dict)
    return tasty_dict
