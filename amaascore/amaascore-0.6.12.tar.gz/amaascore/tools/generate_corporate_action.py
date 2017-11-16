from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.random_utils import random_string
import datetime
from decimal import Decimal
import random

from amaascore.corporate_actions.corporate_action import CorporateAction
from amaascore.corporate_actions.dividend import Dividend
from amaascore.corporate_actions.split import Split
from amaascore.core.reference import Reference

REFERENCE_TYPES = ['CAEF']


def generate_common(asset_manager_id=None, corporate_action_id=None, asset_id=None):

    common = {'asset_manager_id': asset_manager_id or random.randint(1, 1000),
              'corporate_action_id': corporate_action_id or str(random.randint(1, 10000)),
              'asset_id': asset_id or str(random.randint(1, 10000)),
              'record_date': datetime.date(random.randint(2016, 2020), random.randint(1, 12), random.randint(1, 28))
              }

    return common


def generate_corporate_action(asset_manager_id=None, corporate_action_id=None, asset_id=None):

    common = generate_common(asset_manager_id=asset_manager_id, corporate_action_id=corporate_action_id,
                             asset_id=asset_id)
    corporate_action = CorporateAction(**common)
    references = {ref_type: Reference(reference_value=random_string(10)) for ref_type in REFERENCE_TYPES}
    corporate_action.references.update(references)
    return corporate_action


def generate_dividend(asset_manager_id=None, corporate_action_id=None, asset_id=None):
    attributes = generate_common(asset_manager_id=asset_manager_id, corporate_action_id=corporate_action_id,
                                 asset_id=asset_id)
    dividend = Dividend(dividend_rate=Decimal(random.random()).quantize(Decimal('1.00')),
                        dividend_asset_id=random_string(10), **attributes)
    return dividend


def generate_split(asset_manager_id=None, corporate_action_id=None, asset_id=None):
    attributes = generate_common(asset_manager_id=asset_manager_id, corporate_action_id=corporate_action_id,
                                 asset_id=asset_id)
    split = Split(ratio=(random.randint(1, 5), random.randint(1, 5)), **attributes)
    return split


def generate_corporate_actions(asset_manager_ids=[], number=5):
    corporate_actions = []
    for i in range(number):
        corporate_action = generate_corporate_action(asset_manager_id=random.choice(asset_manager_ids))
        corporate_actions.append(corporate_action)
    return corporate_actions
