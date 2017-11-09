from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.random_utils import random_string
import datetime
from decimal import Decimal
import random

from amaascore.core.comment import Comment
from amaascore.core.reference import Reference
from amaascore.transactions.cash_transaction import CashTransaction
from amaascore.transactions.children import Charge, Code, Link, Party, Rate
from amaascore.transactions.enums import TRANSACTION_ACTIONS, CASH_TRANSACTION_TYPES
from amaascore.transactions.mtm_result import MTMResult
from amaascore.transactions.pnl_result import PNLResult
from amaascore.transactions.position import Position
from amaascore.transactions.transaction import Transaction

CHARGE_TYPES = ['Tax', 'Commission']
CODE_TYPES = ['Settle Code', 'Client Classifier']
COMMENT_TYPES = ['Trader']
PARTY_TYPES = ['Prime Broker']
RATE_TYPES = ['Tax', 'Commission']
REFERENCE_TYPES = ['External']


def generate_common(asset_manager_id, asset_book_id, counterparty_book_id, asset_id, quantity, transaction_date,
                    settlement_date, transaction_id, transaction_action, transaction_type, transaction_status):

    common = {'asset_manager_id': asset_manager_id or random.randint(1, 1000),
              'asset_book_id': asset_book_id or random_string(8),
              'counterparty_book_id': counterparty_book_id or random_string(8),
              'asset_id': asset_id or str(random.randint(1, 1000)),
              'quantity': quantity or Decimal(random.randint(0, 5000)),
              'transaction_date': transaction_date or datetime.date.today(),
              'transaction_action': transaction_action or random.choice(list(TRANSACTION_ACTIONS)),
              'transaction_id': transaction_id,
              'transaction_status': transaction_status or 'New',
              'transaction_type': transaction_type or 'Trade'
              }

    common['settlement_date'] = settlement_date or (datetime.timedelta(days=2) + common['transaction_date'])
    return common

def generate_pnl_result(asset_manager_id=None, book_id=None, asset_id=None, period=None,
                        business_date=None, version=None, total_pnl=None, asset_pnl=None, fx_pnl=None,
                        unrealised_pnl=None, realised_pnl=None, message=None, client_id=None,
                        transaction_id=None, pnl_timestamp=None, pnl_status='Active'):
    total_pnl = random.randrange(-100000000, 2000000000)
    asset_pnl = random.randrange(-100000000, 1000000000)
    fx_pnl = total_pnl - asset_pnl
    pnl_result = PNLResult(asset_manager_id=asset_manager_id or random.randint(1, 10000),
                           book_id=book_id or random_string(8),
                           asset_id=asset_id or random_string(10),
                           period=period or random.choice(['YTD', 'MTD', 'DTD']),
                           business_date=business_date or datetime.date.today(),
                           version=version or 1,
                           total_pnl=total_pnl or str(total_pnl),
                           fx_pnl=fx_pnl or str(fx_pnl),
                           asset_pnl=asset_pnl or (asset_pnl),
                           unrealised_pnl=unrealised_pnl,
                           realised_pnl=realised_pnl,
                           message=message or '',
                           transaction_id=transaction_id or random_string(16),
                           pnl_timestamp=pnl_timestamp or datetime.datetime.utcnow(),
                           client_id=client_id or 1,
                           pnl_status=pnl_status)
    return pnl_result

def generate_mtm_result(asset_manager_id=None, book_id=None, mtm_value=None, business_date=None, mtm_timestamp=None,
                        asset_id=None, message=None, client_id=None, mtm_status=None):
    mtm_result = MTMResult(asset_manager_id=asset_manager_id or random.randint(1, 10000), 
                           book_id=book_id or random_string(8),
                           business_date=business_date or datetime.date.today(),
                           mtm_timestamp=mtm_timestamp or datetime.datetime.now(),
                           mtm_value=mtm_value or str(random.random()*100000),
                           asset_id=asset_id or random_string(8),
                           message=message or random_string(80),
                           client_id=client_id or 1,
                           mtm_status=mtm_status or 'Active')
    return mtm_result


def generate_transaction(asset_manager_id=None, asset_book_id=None, counterparty_book_id=None,
                         asset_id=None, quantity=None, transaction_date=None, transaction_id=None,
                         price=None, transaction_action=None, transaction_type=None, settlement_date=None,
                         transaction_status=None, transaction_currency=None, settlement_currency=None,
                         net_affecting_charges=None, charge_currency=None):
    # Explicitly handle price is None (in case price is 0)
    price = Decimal(random.uniform(1.0, 1000.0)).quantize(Decimal('0.01')) if price is None else price
    transaction_currency = transaction_currency or random.choice(['SGD', 'USD'])
    settlement_currency = settlement_currency or transaction_currency or random.choice(['SGD', 'USD'])
    common = generate_common(asset_manager_id=asset_manager_id, asset_book_id=asset_book_id,
                             counterparty_book_id=counterparty_book_id, asset_id=asset_id, quantity=quantity,
                             transaction_date=transaction_date, transaction_id=transaction_id, 
                             transaction_action=transaction_action, transaction_status=transaction_status,
                             transaction_type=transaction_type, settlement_date=settlement_date)

    transaction = Transaction(price=price, transaction_currency=transaction_currency,
                              settlement_currency=settlement_currency, **common)
    charges = {charge_type: Charge(charge_value=Decimal(random.uniform(1.0, 100.0)).quantize(Decimal('0.01')),
                                   currency=charge_currency or random.choice(['USD', 'SGD']),
                                   net_affecting=net_affecting_charges or random.choice([True, False]))
               for charge_type in CHARGE_TYPES}

    links = {'Single': Link(linked_transaction_id=random_string(8)),
             'Multiple': {Link(linked_transaction_id=random_string(8)) for x in range(3)}}

    codes = {code_type: Code(code_value=random_string(8)) for code_type in CODE_TYPES}
    comments = {comment_type: Comment(comment_value=random_string(8)) for comment_type in COMMENT_TYPES}
    parties = {party_type: Party(party_id=random_string(8)) for party_type in PARTY_TYPES}
    rates = {rate_type:
             Rate(rate_value=Decimal(random.uniform(1.0, 100.0)).quantize(Decimal('0.01')))
             for rate_type in RATE_TYPES}
    references = {ref_type: Reference(reference_value=random_string(10)) for ref_type in REFERENCE_TYPES}

    transaction.charges.update(charges)
    transaction.codes.update(codes)
    transaction.comments.update(comments)
    transaction.links.update(links)
    transaction.parties.update(parties)
    transaction.rates.update(rates)
    transaction.references.update(references)
    return transaction


def generate_cash_transaction(asset_manager_id=None, asset_book_id=None, counterparty_book_id=None,
                              asset_id=None, quantity=None, transaction_date=None, transaction_id=None,
                              transaction_action=None, transaction_type=None,
                              transaction_status=None):
    transaction_type = transaction_type or random.choice(list(CASH_TRANSACTION_TYPES))
    common = generate_common(asset_manager_id=asset_manager_id, asset_book_id=asset_book_id,
                             counterparty_book_id=counterparty_book_id, asset_id=asset_id, quantity=quantity,
                             transaction_date=transaction_date, transaction_id=transaction_id,
                             transaction_action=transaction_action, transaction_status=transaction_status,
                             transaction_type=transaction_type)

    transaction = CashTransaction(**common)
    return transaction


def generate_position(asset_manager_id=None, book_id=None, asset_id=None, account_id=None, 
                      accounting_type=None, quantity=None):
    position = Position(asset_manager_id=asset_manager_id or random.randint(1, 1000),
                        book_id=book_id or random_string(8),
                        asset_id=asset_id or str(random.randint(1, 1000)),
                        account_id=random.choice(['Cash', 'Asset']),
                        accounting_type=random.choice(['Transaction Date', 'Settlement Date']),
                        quantity=quantity or Decimal(random.randint(1, 50000)))
    return position


def generate_transactions(asset_manager_ids=[], number=5):
    transactions = []
    for i in range(number):
        transaction = generate_transaction(asset_manager_id=random.choice(asset_manager_ids))
        transactions.append(transaction)
    return transactions


def generate_positions(asset_manager_ids=[], book_ids=[], number=5):
    positions = []
    for i in range(number):
        position = generate_position(asset_manager_id=random.choice(asset_manager_ids),
                                     book_id=random.choice(book_ids) if book_ids else None)
        positions.append(position)
    return positions
