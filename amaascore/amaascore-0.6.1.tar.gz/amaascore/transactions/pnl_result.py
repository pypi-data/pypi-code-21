from decimal import Decimal
from amaascore.core.amaas_model import AMaaSModel


class PNLResult(AMaaSModel):

    def __init__(self, asset_manager_id, book_id, asset_id, period, quantity,
                 business_date, pnl_timestamp, transaction_id, pnl_status='Active',
                 total_pnl=None, asset_pnl=None, fx_pnl=None, 
                 unrealised_pnl=None, realised_pnl=None,
                 message=None, *args, **kwargs):
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
        self.quantity = quantity
        self.message = message
        self.transaction_id = transaction_id
        self.pnl_timestamp = pnl_timestamp

        super(PNLResult, self).__init__(*args, **kwargs)

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, val):
        if not isinstance(val, Decimal) and val is not None:
            self._quantity = Decimal(val)
        else:
            self._quantity = val        

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
        if not isinstance(val, Decimal) and val is not None:
            self._total_pnl = Decimal(val)
        else:
            self._total_pnl = val

    @property
    def fx_pnl(self):
        return self._fx_pnl

    @fx_pnl.setter
    def fx_pnl(self, val):
        if not isinstance(val, Decimal) and val is not None:
            self._fx_pnl = Decimal(val)
        else:
            self._fx_pnl = val

    @property
    def asset_pnl(self):
        return self._asset_pnl

    @asset_pnl.setter
    def asset_pnl(self, val):
        if not isinstance(val, Decimal) and val is not None:
            self._asset_pnl = Decimal(val)
        else:
            self._asset_pnl = val
