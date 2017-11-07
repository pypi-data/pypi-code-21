from decimal import Decimal
from dateutil.parser import parse

import pytz
from amaascore.core.amaas_model import AMaaSModel


class PNLResult(AMaaSModel):

    def __init__(self, asset_manager_id, book_id, asset_id, period,
                 business_date, version, total_pnl, asset_pnl, fx_pnl,
                 unrealised_pnl, realised_pnl, transaction_id, pnl_timestamp, 
                 message='', pnl_status='Active', *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.asset_id = asset_id
        self.book_id = book_id
        self.period = period
        self.business_date = business_date
        self.realised_pnl = realised_pnl
        self.unrealised_pnl = unrealised_pnl
        self.total_pnl = total_pnl
        self.asset_pnl = asset_pnl
        self.fx_pnl = fx_pnl
        self.pnl_status = pnl_status
        self.message = message
        self.transaction_id = transaction_id
        self.version = version
        self.pnl_timestamp = pnl_timestamp

        super(PNLResult, self).__init__(*args, **kwargs)

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, val):
        if val not in ['YTD', 'MTD', 'DTD']:
            raise ValueError("""Unrecognized PnL period %s, expect 
                    period to be one of the following: 'YTD', 'MTD', 'DTD'""" % str(val))
        self._period = val

    @property
    def total_pnl(self):
        return self._total_pnl

    @total_pnl.setter
    def total_pnl(self, val):
        if not isinstance(val, Decimal) and not isinstance(val, str) and val is not None:
            self._total_pnl = Decimal(val)
        else:
            self._total_pnl = val

    @property
    def fx_pnl(self):
        return self._fx_pnl

    @fx_pnl.setter
    def fx_pnl(self, val):
        if not isinstance(val, Decimal) and not isinstance(val, str) and val is not None:
            self._fx_pnl = Decimal(val)
        else:
            self._fx_pnl = val

    @property
    def asset_pnl(self):
        return self._asset_pnl

    @asset_pnl.setter
    def asset_pnl(self, val):
        if not isinstance(val, Decimal) and not isinstance(val, str) and val is not None:
            self._asset_pnl = Decimal(val)
        else:
            self._asset_pnl = val

    
    # NOTE: add more getter and setters for other attributes that may be needed