from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from dateutil.parser import parse
from decimal import Decimal
import sys

from amaascore.assets.asset import Asset

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class BondBase(Asset):

    def __init__(self, asset_manager_id, asset_id, maturity_date, coupon, par, pay_frequency, asset_issuer_id,
                 asset_status, currency, roll_price, display_name, description, country_id, venue_id, issue_date,
                 defaulted, links, references, *args, **kwargs):
        self.asset_class = 'Bond'
        self.coupon = coupon
        self.par = par
        self.pay_frequency = pay_frequency
        self.defaulted = defaulted
        self.maturity_date = maturity_date
        super(BondBase, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=True,
                                       asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                       roll_price=roll_price, display_name=display_name, currency=currency,
                                       description=description, country_id=country_id, venue_id=venue_id,
                                       issue_date=issue_date, links=links, references=references,
                                       *args, **kwargs)

    @property
    def coupon(self):
        if hasattr(self, '_coupon'):
            return self._coupon

    @coupon.setter
    def coupon(self, coupon):
        """
        The coupon paid out by the bond.  Represented as a fraction of 1 (e.g. 0.05 is 5%).
        :param coupon:
        :return:
        """
        if coupon is not None:
            self._coupon = Decimal(coupon)

    @property
    def par(self):
        if hasattr(self, '_par'):
            return self._par

    @par.setter
    def par(self, par):
        """
        The face value of each bond.
        Force this to be Decimal
        :param par:
        :return:
        """
        if par is not None:
            self._par = Decimal(par)

    @property
    def maturity_date(self):
        return self._maturity_date

    @maturity_date.setter
    def maturity_date(self, maturity_date):
        if maturity_date:
            self._maturity_date = parse(maturity_date).date() if isinstance(maturity_date, type_check) \
                else maturity_date


class BondGovernment(BondBase):

    def __init__(self, asset_manager_id, asset_id, coupon, par, pay_frequency, defaulted=False, asset_issuer_id=None,
                 currency=None, maturity_date=date.max, asset_status='Active', roll_price=False, display_name='',
                 description='', country_id=None, venue_id=None, issue_date=date.min,
                 links=None, references=None, *args, **kwargs):
        super(BondGovernment, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                             asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                             roll_price=roll_price, display_name=display_name, currency=currency,
                                             description=description, country_id=country_id, venue_id=venue_id,
                                             maturity_date=maturity_date, links=links, references=references,
                                             coupon=coupon, par=par, issue_date=issue_date, pay_frequency=pay_frequency,
                                             defaulted=defaulted, *args, **kwargs)


class BondCorporate(BondBase):

    def __init__(self, asset_manager_id, asset_id, coupon, par, pay_frequency, defaulted=False, asset_issuer_id=None,
                 currency=None, maturity_date=date.max, asset_status='Active', roll_price=True, display_name='',
                 description='', country_id=None, venue_id=None, issue_date=date.min,
                 links=None, references=None, *args, **kwargs):
        super(BondCorporate, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                            asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                            roll_price=roll_price, display_name=display_name, currency=currency,
                                            description=description, country_id=country_id, venue_id=venue_id,
                                            maturity_date=maturity_date, links=links, references=references,
                                            coupon=coupon, par=par, issue_date=issue_date, pay_frequency=pay_frequency,
                                            defaulted=defaulted, *args, **kwargs)


class BondMortgage(BondBase):

    def __init__(self, asset_manager_id, asset_id, coupon, par, pay_frequency, defaulted=False, asset_issuer_id=None,
                 currency=None, maturity_date=date.max, asset_status='Active', roll_price=True, display_name='',
                 description='', country_id=None, venue_id=None, issue_date=date.min,
                 links=None, references=None, *args, **kwargs):
        super(BondMortgage, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                           asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                           roll_price=roll_price, display_name=display_name, currency=currency,
                                           description=description, country_id=country_id, venue_id=venue_id,
                                           maturity_date=maturity_date, links=links, references=references,
                                           coupon=coupon, par=par, issue_date=issue_date, pay_frequency=pay_frequency,
                                           defaulted=defaulted, *args, **kwargs)
