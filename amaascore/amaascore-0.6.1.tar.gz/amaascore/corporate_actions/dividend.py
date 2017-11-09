from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal

from amaascore.corporate_actions.corporate_action import CorporateAction


class Dividend(CorporateAction):

    def __init__(self, asset_manager_id, corporate_action_id, record_date, dividend_rate, dividend_asset_id,
                 corporate_action_status='Open', asset_id=None, party_id=None, declared_date=None, settlement_date=None,
                 elective=False, message=None, description='', references=None, *args, **kwargs):
        self.dividend_rate = dividend_rate
        self.dividend_asset_id = dividend_asset_id
        super(Dividend, self).__init__(asset_manager_id=asset_manager_id, corporate_action_id=corporate_action_id,
                                       record_date=record_date, corporate_action_status=corporate_action_status,
                                       asset_id=asset_id, party_id=party_id, declared_date=declared_date,
                                       settlement_date=settlement_date, elective=elective, message=message,
                                       description=description, references=references, *args, **kwargs)

    @property
    def dividend_rate(self):
        if hasattr(self, '_dividend_rate'):
            return self._dividend_rate

    @dividend_rate.setter
    def dividend_rate(self, value):
        """
        The rate per share to pay out for the dividend
        :param value:
        :return:
        """
        if value:
            self._dividend_rate = Decimal(value)
