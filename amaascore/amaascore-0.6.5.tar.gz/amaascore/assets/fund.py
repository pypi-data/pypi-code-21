from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, date
from dateutil.parser import parse
from decimal import Decimal
import sys

from amaascore.assets.asset import Asset

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Fund(Asset):

    def __init__(self, asset_manager_id, asset_id, fund_type, nav=None, expense_ratio=None, net_assets=None,
                 asset_issuer_id=None, asset_status='Active', roll_price=False, display_name='', description='',
                 country_id=None, venue_id=None, currency=None, creation_date=None,
                 links=None, references=None,
                 *args, **kwargs):
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'Fund'
        self.fund_type = fund_type
        self.creation_date = creation_date
        self.nav = nav
        self.expense_ratio = expense_ratio
        self.net_assets = net_assets
        super(Fund, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=True,
                                   asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                   display_name=display_name, roll_price=roll_price,
                                   description=description, country_id=country_id, venue_id=venue_id,
                                   currency=currency, links=links, references=references, *args, **kwargs)

    #  Perhaps this comes from the linked Fund
    @property
    def creation_date(self):
        if hasattr(self, '_creation_date'):
            return self._creation_date

    @creation_date.setter
    def creation_date(self, value):
        """
        The date on which the bond was issued.
        :param creation_date:
        :return:
        """
        if value:
            self._creation_date = parse(value).date() if isinstance(value, type_check) else value

    @property
    def nav(self):
        if hasattr(self, '_nav'):
            return self._nav

    @nav.setter
    def nav(self, nav):
        """

        :param nav:
        :return:
        """
        if nav is not None:
            self._nav = Decimal(nav)

    @property
    def expense_ratio(self):
        if hasattr(self, '_expense_ratio'):
            return self._expense_ratio

    @expense_ratio.setter
    def expense_ratio(self, expense_ratio):
        """

        :param expense_ratio:
        :return:
        """
        if expense_ratio is not None:
            self._expense_ratio = Decimal(expense_ratio)

    @property
    def net_assets(self):
        if hasattr(self, '_net_assets'):
            return self._net_assets

    @net_assets.setter
    def net_assets(self, net_assets):
        """

        :param net_assets: An integer representing the net assets of the fund
        :return:
        """
        if net_assets is not None:
            self._net_assets = net_assets

    @property
    def fund_type(self):
        return self._fund_type

    @fund_type.setter
    def fund_type(self, fund_type):
        """

        :param fund_type: One of ['Open', 'Closed', 'ETF']
        :return:
        """
        if fund_type in ['Open', 'Closed', 'ETF']:
            self._fund_type = fund_type
