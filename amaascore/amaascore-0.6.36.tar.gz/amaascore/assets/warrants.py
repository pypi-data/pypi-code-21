from datetime import datetime, date
from dateutil import parser
from dateutil.parser import parse

from amaascore.assets.asset import Asset
from amaascore.assets.equity import Equity

class Warrant(Equity):

    @staticmethod
    def mandatory_attributes():
        return set()

    @staticmethod
    def additional_attributes():
        return set()

    def __init__(self, asset_manager_id, asset_id, client_id, asset_issuer_id=None, asset_status='Active',
                 description='', country_id=None, venue_id=None, currency=None, issue_date=date.min,
                 share_class=None, additional=None, display_name='', roll_price=False,
                 underlying_price=None, strike_price=None, cv_ratio=None,
                 exercise_type=None, expiration_date=None, first_exercise_date=None,
                 last_trade_date=None, issue_price=None, issued_quant=None,
                 outstanding=None, issuer=None, settlement_type=None, warrant_type=None, 
                 links=None, references=None, *args, **kwargs):
        super(Warrant, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, client_id=client_id, asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                     description=description, country_id=country_id, venue_id=venue_id, currency=currency, issue_date=issue_date,
                                     share_class=share_class, additional=additional, display_name=display_name, roll_price=roll_price,
                                     links=links, references=references, *args, **kwargs)

        #self.asset_class = 'Warrant'

        self.underlying_price = underlying_price
        self.strike_price = strike_price
        self.cv_ratio = cv_ratio
        self.exercise_type = exercise_type
        self.expiration_date = expiration_date
        self.first_exercise_date = first_exercise_date
        self.last_trade_date = last_trade_date
        self.issue_price = issue_price
        self.issued_quant = issued_quant
        self.outstanding = outstanding
        self.issuer = issuer
        self.settlement_type = settlement_type
        self.warrant_type = warrant_type

    @property
    def underlying_price(self):
        return self._underlying_price

    @underlying_price.setter
    def underlying_price(self, underlying_price):
        self._underlying_price = underlying_price
    
    @property
    def strike_price(self):
        return self._strike_price

    @strike_price.setter
    def strike_price(self, strike_price):
        self._strike_price = strike_price

    @property
    def cv_ratio(self):
        return self._cv_ratio

    @cv_ratio.setter
    def cv_ratio(self, cv_ratio):
        self._cv_ratio = cv_ratio

    @property
    def exercise_type(self):
        return self._exercise_type

    @exercise_type.setter
    def exercise_type(self, exercise_type):
        if exercise_type is None:
            self._exercise_type = None
        else:
            if exercise_type not in ['European', 'American']:
                raise ValueError("Invalid exercise_type European/American: %s" % exercise_type)
            self._exercise_type = exercise_type

    @property
    def expiration_date(self):
        return self._expiration_date

    @expiration_date.setter
    def expiration_date(self, expiration_date):
        self._expiration_date = expiration_date

    @property
    def first_exercise_date(self):
        return self._first_exercise_date

    @first_exercise_date.setter
    def first_exercise_date(self, first_exercise_date):
        self._first_exercise_date = first_exercise_date
    
    @property
    def last_trade_date(self):
        return self._last_trade_date

    @last_trade_date.setter
    def last_trade_date(self, last_trade_date):
        self._last_trade_date = last_trade_date

    @property
    def issue_price(self):
        return self._issue_price

    @issue_price.setter
    def issue_price(self, issue_price):
        self._issue_price = issue_price

    @property
    def issued_quant(self):
        return self._issued_quant

    @issued_quant.setter
    def issued_quant(self, issued_quant):
        self._issued_quant = issued_quant
    
    @property
    def outstanding(self):
        return self._outstanding

    @outstanding.setter
    def outstanding(self, outstanding):
        self._outstanding = outstanding

    @property
    def issuer(self):
        return self._issuer

    @issuer.setter
    def issuer(self, issuer):
        self._issuer = issuer
        
    @property
    def settlement_type(self):
        return self._settlement_type

    @settlement_type.setter
    def settlement_type(self, settlement_type):
        if settlement_type is None:
            self._settlement_type = None
        else:
            if settlement_type not in ['Cash', 'Physical']:
                raise ValueError("Invalid settlement_type Cash/Physical" % settlement_type)
            self._settlement_type = settlement_type

    @property
    def warrant_type(self):
        return self._warrant_type

    @warrant_type.setter
    def warrant_type(self, warrant_type):
        if warrant_type is None:
            self._warrant_type = None
        else:
            if warrant_type not in ["Covered", "Traditional"]:
                raise ValueError("Invalid warrant_type Covered/Traditional: %s" % warrant_type)
            self._warrant_type = warrant_type

