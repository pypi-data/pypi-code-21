from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date, datetime
from dateutil.parser import parse
from decimal import Decimal
import pytz
import sys

from amaascore.core.amaas_model import AMaaSModel

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class FXRate(AMaaSModel):

    def __init__(self, asset_manager_id, asset_id, business_date, rate_timestamp, rate, rate_type, active=True,
                 *args, **kwargs):
        """

        :param asset_manager_id: The asset_manager_id who owns this price
        :param asset_id:  The asset_id for which we are providing a price
        :param business_date:  The business date for which this is the EOD price
        :param rate_timestamp: The specific point in time at which the rate was taken
        :param rate: The rate itself
        :param rate_type: An identifying "type" for the rate in case there are multiple rates for the same time period
        :param active: A boolean indicator of whether this rate is valid, or whether it was deactivated
        """
        self.asset_manager_id = asset_manager_id
        self.asset_id = asset_id
        self.business_date = business_date
        self.rate_timestamp = rate_timestamp
        self.rate_type = rate_type
        self.rate = rate
        self.active = active
        super(FXRate, self).__init__(*args, **kwargs)

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, value):
        """
        Force the rate to always be a decimal
        :param value:
        :return:
        """
        if value is not None:
            self._rate = Decimal(value)

    @property
    def business_date(self):
        return self._business_date

    @business_date.setter
    def business_date(self, business_date):
        """
        Force the business_date to always be a date
        :param business_date:
        :return:
        """
        if business_date is not None:
            if isinstance(business_date, type_check):
                self._business_date = parse(business_date).date()
            else:
                self._business_date= business_date

    @property
    def rate_timestamp(self):
        return self._rate_timestamp

    @rate_timestamp.setter
    def rate_timestamp(self, rate_timestamp):
        """
        Force the rate_timestamp to be a datetime
        :param rate_timestamp:
        :return:
        """
        if rate_timestamp is not None:
            if isinstance(rate_timestamp, (str, type_check)):
                rate_timestamp = parse(rate_timestamp).replace(tzinfo=pytz.utc)
            if type(rate_timestamp) == date:
                rate_timestamp = datetime.combine(rate_timestamp, datetime.min.time()).replace(tzinfo=pytz.utc)
            if not rate_timestamp.tzinfo:
                raise ValueError('Cannot set an FX rate timestamp without a timezone')
            self._rate_timestamp = rate_timestamp
