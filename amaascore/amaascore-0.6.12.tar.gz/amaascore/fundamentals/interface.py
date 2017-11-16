from __future__ import absolute_import, division, print_function, unicode_literals

from dateutil.parser import parse
import logging

from amaascore.config import ENVIRONMENT
from amaascore.core.interface import Interface


class FundamentalsInterface(Interface):

    def __init__(self, environment=ENVIRONMENT, logger=None, endpoint=None, username=None, password=None):
        logger = logger or logging.getLogger(__name__)
        super(FundamentalsInterface, self).__init__(endpoint=endpoint,
                                                    endpoint_type='fundamentals',
                                                    environment=environment,
                                                    username=None, 
                                                    password=None,
                                                    logger=logger)

    def countries(self, country_code=None):
        log_msg = 'Get Country: %s' % country_code if country_code else 'Get All Countries'
        self.logger.info(log_msg)
        url = '%s/countries' % self.endpoint
        params = {'country_code': country_code} if country_code else {}
        response = self.session.get(url, params=params)
        if response.ok:
            self.logger.info('Successfully retrieved country(s)')
            return response.json()
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def holidays(self, country_codes=[], years=[]):
        country_codes = ','.join(country_codes)
        years = ','.join([str(year) for year in years])
        self.logger.info('Get Holiday Calendar for: %s for years: %s', country_codes, years)
        url = '%s/holidays' % self.endpoint
        params = {'country_codes': country_codes,
                  'years': years}

        response = self.session.get(url, params=params)
        if response.ok:
            self.logger.info('Successfully retrieved holidays')
            return response.json()
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def calc_business_date(self, start_date, country_codes, offset, invalid_dates=None):
        self.logger.info('Calculating business date')
        url = '%s/business-date' % self.endpoint
        params = {'start_date': start_date.isoformat(),
                  'country_codes': ','.join(country_codes),
                  'offset': offset}
        if invalid_dates:
            params['invalid_dates'] = ','.join([invalid_date.isoformat() for invalid_date in invalid_dates])
        response = self.session.get(url, params=params)
        if response.ok:
            self.logger.info('Successfully calculated business date')
            business_date = response.json().get('business_date')
            business_date = parse(business_date).date()
            return business_date
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def get_date_info(self, business_date, country_codes):
        self.logger.info('Getting information about date: %s', business_date)
        url = '%s/date-info/%s' % (self.endpoint, business_date.isoformat())
        params = {'country_codes': ','.join(country_codes)}
        response = self.session.get(url, params=params)
        if response.ok:
            self.logger.info('Successfully got information about date')
            return response.json()
        else:
            self.logger.error(response.text)
            response.raise_for_status()