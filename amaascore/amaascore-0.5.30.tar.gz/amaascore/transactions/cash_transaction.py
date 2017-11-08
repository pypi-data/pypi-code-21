from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.transactions.transaction import Transaction


class CashTransaction(Transaction):

    def __init__(self, asset_manager_id, asset_book_id, counterparty_book_id, transaction_action,
                 asset_id, quantity, transaction_date, settlement_date, asset=None, execution_time=None,
                 transaction_type='Trade', transaction_id=None, transaction_status='New',
                 charges=None, codes=None, comments=None, links=None, parties=None,
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

        super(CashTransaction, self).__init__(asset_manager_id=asset_manager_id,
                                              asset_book_id=asset_book_id,
                                              counterparty_book_id=counterparty_book_id,
                                              transaction_action=transaction_action,
                                              asset_id=asset_id,
                                              quantity=quantity,
                                              transaction_date=transaction_date,
                                              settlement_date=settlement_date,
                                              price=1,
                                              transaction_currency=asset_id,
                                              settlement_currency=asset_id,
                                              asset=asset,
                                              execution_time=execution_time,
                                              transaction_type=transaction_type,
                                              transaction_id=transaction_id,
                                              transaction_status=transaction_status,
                                              charges=charges,
                                              codes=codes,
                                              comments=comments,
                                              links=links,
                                              parties=parties,
                                              rates=rates,
                                              references=references,
                                              *args, **kwargs)
