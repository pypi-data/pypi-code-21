from __future__ import absolute_import, division, print_function, unicode_literals

import copy
import datetime
from dateutil.parser import parse
from decimal import Decimal
import sys
import uuid

from amaascore.error_messages import ERROR_LOOKUP
from amaascore.exceptions import TransactionNeedsSaving
from amaascore.core.amaas_model import AMaaSModel
from amaascore.core.comment import Comment
from amaascore.core.reference import Reference
from amaascore.transactions.children import Charge, Code, Link, Party, Rate
from amaascore.transactions.enums import TRANSACTION_ACTIONS, TRANSACTION_STATUSES, TRANSACTION_TYPES

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Transaction(AMaaSModel):

    @staticmethod
    def children():
        """ A dict of which of the attributes are collections of other objects, and what type """
        return {'charges': Charge, 'codes': Code, 'comments': Comment, 'links': Link, 'parties': Party,
                'rates': Rate, 'references': Reference}

    def __init__(self, asset_manager_id, asset_book_id, counterparty_book_id, transaction_action, asset_id, quantity,
                 transaction_date, settlement_date, price, transaction_currency, settlement_currency=None,
                 asset=None, execution_time=None, transaction_type='Trade', transaction_id=None,
                 transaction_status='New', charges=None, codes=None, comments=None, links=None, parties=None,
                 rates=None, references=None, *args, **kwargs):
        """

        :param asset_manager_id:
        :param asset_book_id:
        :param counterparty_book_id:
        :param transaction_action:
        :param asset_id:
        :param quantity:
        :param transaction_date:
        :param settlement_date:
        :param price:
        :param transaction_currency:
        :param settlement_currency: The currency in which the transaction will be settled.  Defaults to the
        transaction_currency if not specified.
        :param asset:
        :param execution_time:
        :param transaction_type:
        :param transaction_id:
        :param transaction_status:
        :param charges:
        :param codes:
        :param comments:
        :param links:
        :param parties:
        :param rates:
        :param references:
        :param args:
        :param kwargs:
        """

        self.transaction_id = transaction_id or uuid.uuid4().hex
        self.asset_manager_id = asset_manager_id
        self.asset_book_id = asset_book_id
        self.counterparty_book_id = counterparty_book_id
        self.transaction_action = transaction_action
        self.asset_id = asset_id  # This is duplicated on the child asset.  Remove?
        self.quantity = quantity
        self.transaction_date = transaction_date
        self.settlement_date = settlement_date
        self.price = price
        self.transaction_currency = transaction_currency
        self.settlement_currency = settlement_currency or transaction_currency
        self.transaction_type = transaction_type
        self.transaction_status = transaction_status

        # Cannot be in method signature or the value gets bound to the constructor call
        self.execution_time = execution_time or datetime.datetime.utcnow()

        # Defaults are here not in constructor for mutability reasons.
        self.charges = charges.copy() if charges else {}
        self.codes = codes.copy() if codes else {}
        self.comments = comments.copy() if comments else {}
        self.links = links.copy() if links else {}
        self.parties = parties.copy() if parties else {}
        self.rates = rates.copy() if rates else {}
        self.references = references.copy() if references else {}
        self.references['AMaaS'] = Reference(reference_value=self.transaction_id)  # Upserts the AMaaS Reference

        self.postings = []
        self.asset = asset
        super(Transaction, self).__init__(*args, **kwargs)

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        """
        Force the quantity to always be a decimal
        :param value:
        :return:
        """
        self._quantity = Decimal(value)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        """
        Force the price to always be a decimal
        :param value:
        :return:
        """
        self._price = Decimal(value)

    @property
    def transaction_currency(self):
        return self._transaction_currency

    @transaction_currency.setter
    def transaction_currency(self, transaction_currency):
        if transaction_currency and len(transaction_currency) == 3:
            self._transaction_currency = transaction_currency
        else:
            raise ValueError(ERROR_LOOKUP['currency_invalid'] % (transaction_currency,
                                                                 self.transaction_id,
                                                                 self.asset_manager_id))

    @property
    def settlement_currency(self):
        return self._settlement_currency

    @settlement_currency.setter
    def settlement_currency(self, settlement_currency):
        if settlement_currency and len(settlement_currency) == 3:
            self._settlement_currency = settlement_currency
        else:
            raise ValueError(ERROR_LOOKUP['currency_invalid'] % (settlement_currency,
                                                                 self.transaction_id,
                                                                 self.asset_manager_id))

    @property
    def transaction_date(self):
        return self._transaction_date

    @transaction_date.setter
    def transaction_date(self, value):
        """
        Force the transaction_date to always be a date
        :param value:
        :return:
        """
        if value:
            self._transaction_date = parse(value).date() if isinstance(value, type_check) else value

    @property
    def settlement_date(self):
        return self._settlement_date

    @settlement_date.setter
    def settlement_date(self, value):
        """
        Force the settlement_date to always be a date
        :param value:
        :return:
        """
        if value:
            self._settlement_date = parse(value).date() if isinstance(value, type_check) else value

    @property
    def execution_time(self):
        return self._execution_time

    @execution_time.setter
    def execution_time(self, value):
        """
        Force the execution_time to always be a datetime
        :param value:
        :return:
        """
        if value:
            self._execution_time = parse(value) if isinstance(value, type_check) else value

    @property
    def gross_settlement(self):
        if hasattr(self, '_gross_settlement'):
            return self.__gross_settlement
        return self.quantity * self.price

    @gross_settlement.setter
    def gross_settlement(self, gross_settlement):
        """

        :param gross_settlement:
        :return:
        """
        if gross_settlement:
            self._gross_settlement = Decimal(gross_settlement)

    @property
    def net_settlement(self):
        if hasattr(self, '_net_settlement'):
            return self._net_settlement
        return self.gross_settlement - self.charges_net_effect()

    @net_settlement.setter
    def net_settlement(self, net_settlement):
        """

        :param gross_settlement:
        :return:
        """
        if net_settlement:
            self._net_settlement = Decimal(net_settlement)

    @property
    def transaction_action(self):
        if hasattr(self, '_transaction_action'):
            return self._transaction_action

    @transaction_action.setter
    def transaction_action(self, transaction_action):
        """

        :param transaction_action: The action that this transaction is recording - e.g. Buy, Deliver
        :return:
        """
        if transaction_action not in TRANSACTION_ACTIONS:
            raise ValueError(ERROR_LOOKUP.get('transaction_action_invalid') % (transaction_action, self.transaction_id,
                                                                               self.asset_manager_id))
        else:
            self._transaction_action = transaction_action

    @property
    def transaction_status(self):
        if hasattr(self, '_transaction_status'):
            return self._transaction_status

    @transaction_status.setter
    def transaction_status(self, transaction_status):
        """

        :param transaction_status: The status of the transaction - e.g. New, Netted
        :return:
        """
        if transaction_status not in TRANSACTION_STATUSES:
            raise ValueError(ERROR_LOOKUP.get('transaction_status_invalid') % (transaction_status, self.transaction_id,
                                                                               self.asset_manager_id))
        else:
            self._transaction_status = transaction_status

    @property
    def transaction_type(self):
        if hasattr(self, '_transaction_type'):
            return self._transaction_type

    @transaction_type.setter
    def transaction_type(self, transaction_type):
        """

        :param transaction_type: The type of transaction that we are recording - e.g. Trade, Payment, Coupon
        :return:
        """
        if transaction_type not in TRANSACTION_TYPES:
            raise ValueError(ERROR_LOOKUP.get('transaction_type_invalid') % (transaction_type, self.transaction_id,
                                                                             self.asset_manager_id))
        else:
            self._transaction_type = transaction_type

    def charges_net_effect(self):
        """
        The total effect of the net_affecting charges (note affect vs effect here).

        Currently this is single currency only (AMAAS-110).

        Cast to Decimal in case the result is zero (no net_affecting charges).

        :return:
        """
        return Decimal(sum([charge.charge_value for charge in self.charges.values()
                            if charge.net_affecting]))

    def charge_types(self):
        """
        TODO - are these helper functions useful?
        :return:
        """
        return self.charges.keys()

    def code_types(self):
        """
        TODO - are these helper functions useful?
        :return:
        """
        return self.codes.keys()

    def rate_types(self):
        """
        TODO - are these helper functions useful?
        :return:
        """
        return self.rates.keys()
    
    def reference_types(self):
        """
        TODO - are these helper functions useful?
        :return:
        """
        return self.references.keys()

    def __str__(self):
        return "Transaction object - ID: %s" % self.transaction_id

    @property
    def postings(self):
        if hasattr(self, '_postings'):
            return self._postings
        else:
            raise TransactionNeedsSaving

    @postings.setter
    def postings(self, postings):
        """
        TODO - when do we save this from AMaaS Core?
        :param postings:
        :return:
        """
        if postings:
            self._postings = postings

    # Upsert methods for safely adding children - this is more important for cases where we trigger action when there
    # is a change, e.g. for the case of a @property on the collection.  Since we don't have that case yet for
    # transactions, I have not yet filled out all of these.
    def upsert_code(self, code_type, code):
        codes = copy.deepcopy(self.codes)
        codes.update({code_type: code})
        self.codes = codes

    def upsert_link_set(self, link_type, link_set):
        """
        Remove an item altogether by setting link_list to None.
        Currently, only links can contain multiple children of the same type.
        :param link_type:
        :param link_set:
        :return:
        """
        if link_set is None:
            self.links.pop(link_type, None)
            return
        links = copy.deepcopy(self.links)
        links.update({link_type: link_set})
        self.links = links

    def add_link(self, link_type, linked_transaction_id):
        new_link = Link(linked_transaction_id=linked_transaction_id)
        link_set = self.links.get(link_type)
        if link_set:
            if not isinstance(link_set, set):
                link_set = {link_set}
            link_set.add(new_link)
        else:
            link_set = new_link
        self.upsert_link_set(link_type=link_type, link_set=link_set)

    def remove_link(self, link_type, linked_transaction_id):
        link_set = self.links.get(link_type)
        if not link_set:
            raise KeyError(ERROR_LOOKUP.get('transaction_link_not_found'))
        if isinstance(link_set, Link):
            if link_set.linked_transaction_id == linked_transaction_id:
                link_set = None
            else:
                raise KeyError(ERROR_LOOKUP.get('transaction_link_not_found'))
        else:
            output = [link for link in link_set if link.linked_transaction_id == linked_transaction_id]
            if output:
                link_set.remove(output[0])
            else:
                raise KeyError(ERROR_LOOKUP.get('transaction_link_not_found'))
        self.upsert_link_set(link_type=link_type, link_set=link_set)
