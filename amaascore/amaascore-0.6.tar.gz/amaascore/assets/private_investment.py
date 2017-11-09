from datetime import datetime, date
from dateutil.parser import parse
from decimal import Decimal
import sys

from amaascore.assets.asset import Asset
from amaascore.assets.enums import PRIVATE_INVESTMENT_CATEGORY, PRIVATE_INVESTMENT_SHARE_TYPE,\
    PRIVATE_INVESTMENT_SUBCATEGORY

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class PrivateInvestment(Asset):

    def __init__(self, asset_manager_id, asset_id, client_id, asset_issuer_id=None,
                 asset_status='Active', display_name='', roll_price=True,
                 description='', country_id=None, venue_id=None, currency=None, additional=None,
                 comments=None, links=None, references=None,
                 category=None, sub_category=None, investment_date=None, num_shares=None,
                 price_share=None, share_class=None, series=None, share_type=None, coupon=None,
                 coupon_freq=None,
                 upfront_fee=None, exit_fee=None, management_fee=None, performance_fee=None,
                 hurdle=None, margin=None, high_water_mark=None, maturity_date=None,
                 lock_up_period=None, investment_term=None,
                 *args, **kwargs):
        if not hasattr(self, 'asset_class'):  # More specific child class may have already set this
            self.asset_class = 'PrivateInvestment'
        self.category = category
        self.sub_category = sub_category
        self.investment_date = investment_date
        self.num_shares = num_shares
        self.price_share = price_share
        self.share_class = share_class
        self.series = series
        self.share_type = share_type
        self.coupon = coupon
        self.coupon_freq = coupon_freq
        self.upfront_fee = upfront_fee  # These fees should probably be on the Transaction.  TODO.
        self.exit_fee = exit_fee  # These fees should probably be on the Transaction.  TODO.
        self.management_fee = management_fee  # These fees should probably be on the Transaction.  TODO.
        self.performance_fee = performance_fee  # These fees should probably be on the Transaction.  TODO.
        self.hurdle = hurdle
        self.margin = margin
        self.high_water_mark = high_water_mark
        self.maturity_date = maturity_date
        self.lock_up_period = lock_up_period
        self.investment_term = investment_term
        super(PrivateInvestment, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                                fungible=False, asset_issuer_id=asset_issuer_id,
                                                asset_status=asset_status, display_name=display_name,
                                                roll_price=roll_price, description=description,
                                                country_id=country_id, venue_id=venue_id,
                                                currency=currency,
                                                comments=comments, links=links, references=references,
                                                client_id=client_id, additional=additional, *args, **kwargs)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        if category in PRIVATE_INVESTMENT_CATEGORY:
            self._category=category
        else:
            raise ValueError('Invalid input of category, please indicate Others if %s not in our list' % category)

    @property
    def sub_category(self):
        return self._sub_category

    @sub_category.setter
    def sub_category(self, sub_category):
        category = self._category
        if category in PRIVATE_INVESTMENT_SUBCATEGORY.keys():
            if sub_category in PRIVATE_INVESTMENT_SUBCATEGORY[category]:
                self._sub_category = sub_category
            else:
                raise ValueError('Invalid input of sub_category: %s' % sub_category)
        else:
            raise ValueError('please set up category correctly')

    @property
    def investment_date(self):
        return self._investment_date

    @investment_date.setter
    def investment_date(self, investment_date):
        if investment_date:
            self._investment_date = parse(investment_date).date() if isinstance(investment_date, type_check)\
                else investment_date

    @property
    def num_shares(self):
        return self._num_shares

    @num_shares.setter
    def num_shares(self, num_shares):
        if isinstance(num_shares, (str, int)):
            self._num_shares = int(num_shares)
        else:
            raise ValueError("num_shares should be an integer :%s" % num_shares)

    @property
    def price_share(self):
        return self._price_share

    @price_share.setter
    def price_share(self, price_share):
        if price_share:
            self._price_share = Decimal(price_share)

    @property
    def share_class(self):
        return self._share_class

    @share_class.setter
    def share_class(self, share_class):
        self._share_class = share_class

    @property
    def share_type(self):
        return self._share_type

    @share_type.setter
    def share_type(self, share_type):
        if share_type in PRIVATE_INVESTMENT_SHARE_TYPE:
            self._share_type = share_type
        else:
            raise ValueError('Invalid input of share_type %s not in our list' % share_type)

    @property
    def maturity_date(self):
        return self._maturity_date

    @maturity_date.setter
    def maturity_date(self, maturity_date):
        if maturity_date:
            self._maturity_date = parse(maturity_date).date() if isinstance(maturity_date, type_check)\
                else maturity_date

    @property
    def lock_up_period(self):
        return self._lock_up_period

    @lock_up_period.setter
    def lock_up_period(self, lock_up_period):
        """ This lockup period is in months.  This might change to a relative delta."""
        try:
            if isinstance(lock_up_period, (str, int)):
                self._lock_up_period = int(lock_up_period)
        except Exception:
            raise ValueError('invalid input of lock up period %s, cannot be converted to an int' %
                             lock_up_period)
    @property
    def investment_term(self):
        return self._investment_term

    @investment_term.setter
    def investment_term(self, investment_term):
        """ This investment term is in months.  This might change to a relative delta."""
        try:
            if isinstance(investment_term, (str, int)):
                self._investment_term = int(investment_term)
        except Exception:
            raise ValueError('invalid input of investment type %s, cannot be converted to an int' %
                             investment_term)
