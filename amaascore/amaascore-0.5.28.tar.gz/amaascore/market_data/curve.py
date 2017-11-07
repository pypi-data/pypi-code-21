from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date, datetime
from dateutil.parser import parse
from decimal import Decimal
import sys
import pytz
import json

from amaascore.core.amaas_model import AMaaSModel

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Curve(AMaaSModel):

    def __init__(self, asset_manager_id, asset_id, fixing_type, business_date, curve_timestamp, curve_rates, client_id, curve_type, additional, active=True,
                  *args, **kwargs):
        """

        :param asset_manager_id: The asset_manager_id of the asset for which we have the price.  Can be 0 for shared.
        :param asset_id: The FX pair for which this is the rate
        :param business_date: The business date for which this rate is used
        :param curve_timestamp: The timestamp for which this curve rate is valid
        :param curve_rates: The rates data points on curve, stored in json format
        :param curve_type: The type of curve, e.g. fx forward curve, interest rate curve etc.
        :param fixing_type: The fixing type of curve, EOD fixing or specific fixing like JPY forward curve at Tokyo closing
        :param active: The boolean status of the rate.  This is to allow rate corrections.
        :param additiona: any additional information about the curve
        """
        self.asset_manager_id = asset_manager_id
        self.asset_id = asset_id
        self.business_date = business_date
        self.curve_timestamp = curve_timestamp
        self.curve_type = curve_type
        self.curve_rates = curve_rates
        self.fixing_type = fixing_type
        self.active = active
        self.client_id = client_id
        self.additional = additional
        super(Curve, self).__init__(*args, **kwargs)
        

    def tenor_dates(self):
        additional = json.loads(self._additional)
        td = additional.get('tenor_dates')
        if td is None:
            raise ValueError("Error in retrieving tenor dates from database for %s on %s" %(self.asset_id, self.business_date))
        tenor_dates = {}     
        for tenor, date_str in td.items():
            date_elements = date_str.split('-')
            tenor_dates[tenor] = date(int(date_elements[0]), int(date_elements[1]), int(date_elements[2]))
        return tenor_dates


    @property
    def curve_rates(self):
        return self._curve_rates

    @curve_rates.setter
    def curve_rates(self, curve_rates):
        """
        :param curve_rates:
        :return:
        """
        if curve_rates is not None:
            if isinstance(curve_rates, str):
                self._curve_rates = curve_rates
            else:
                try:
                    self._curve_rates = json.dumps(curve_rates)
                except TypeError:
                    raise TypeError('Passed in curve rates object are not json serializable.Please check the format')

    @property
    def additional(self):
        return self._additional

    @additional.setter
    def additional(self, additional):
        if additional is not None:
            try:
                self._additional = json.dumps(additional)
            except TypeError:
                raise TypeError('The passed in "Additional" field is not json serializable.')
    @property
    def curve_timestamp(self):
        return self._curve_timestamp

    @curve_timestamp.setter
    def curve_timestamp(self, curve_timestamp):
        """
        Force the timestamp to be a datetime
        :param curve_timestamp:
        :return:
        """
        if curve_timestamp is not None:
            curve_timestamp = str(curve_timestamp)
            if isinstance(curve_timestamp, str):
                curve_timestamp = parse(curve_timestamp).replace(tzinfo=pytz.utc)
            if type(curve_timestamp) == date:
                curve_timestamp = datetime.combine(curve_timestamp, datetime.min.time()).replace(tzinfo=pytz.utc)
            if not curve_timestamp.tzinfo:
                raise ValueError('Cannot set a curve without a timezone')            
            if curve_timestamp > datetime.utcnow().replace(tzinfo=pytz.utc):
                raise ValueError('Cannot set a curve in the future: %s' % curve_timestamp.isoformat())
            self._curve_timestamp = curve_timestamp

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
            if isinstance(business_date, str):
                self._business_date = parse(business_date).date()
            else:
                self._business_date= business_date   