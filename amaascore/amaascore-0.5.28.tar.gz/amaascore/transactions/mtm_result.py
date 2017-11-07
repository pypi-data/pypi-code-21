from decimal import Decimal
from dateutil.parser import parse

import pytz
from amaascore.core.amaas_model import AMaaSModel


class MTMResult(AMaaSModel):

    @staticmethod
    def stored_attributes():
        return {'asset_manager_id', 'book_id', 'mtm_value', 'asset_id',
                'business_date', 'mtm_timestamp', 'message', 'version',
                'mtm_status'}

    @staticmethod
    def lambda_calculated_attributes():
        """
        These fields are calculated internally.  Do not set manually.
        If set manually they will be overridden when the transaction
        is persisted.
        :return:
        """
        return {'client_id', 'created_by', 'updated_by'}


    def __init__(self, asset_manager_id, book_id, business_date, mtm_timestamp, asset_id, 
                 message='', client_id=None, mtm_value=None, mtm_status='Active', *args, **kwargs):
        self.client_id=client_id
        self.asset_manager_id=asset_manager_id 
        self.asset_id=asset_id
        self.book_id=book_id
        self.mtm_value=mtm_value
        self.business_date=business_date
        self.mtm_timestamp=mtm_timestamp 
        self.message=message
        self.mtm_status=mtm_status

        super(MTMResult, self).__init__(*args, **kwargs)

    @property
    def mtm_timestamp(self):
        return self._mtm_timestamp

    @mtm_timestamp.setter
    def mtm_timestamp(self, value):
        if value:
            mtm_timestamp = parse(value) if isinstance(value, str) else value
            self._mtm_timestamp = mtm_timestamp.replace(tzinfo=pytz.UTC) \
                if not mtm_timestamp.tzinfo else mtm_timestamp

    @property
    def mtm_value(self):
        return self._mtm_value

    @mtm_value.setter
    def mtm_value(self, val):
        if not isinstance(val, Decimal) and val is not None:
            self._mtm_value = Decimal(val)
        else:
            self._mtm_value = val