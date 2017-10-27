"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        econsens3.py -- Sensor class for econ sens3

    FIRST RELEASE
        2017-07-03  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""
import logging

import requests

from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from messgeraet_anzapfen.sensor import Sensor, MeasurementError

_logger = logging.getLogger(__name__)

__all__ = ['EconSens3']


class EconSens3(Sensor):
    """econ sens3 is an energie data logging device"""

    config_keys = ['url', 'endpoint']

    def measure(self):
        try:
            self.read_sensor_data()
            self.data = self.parse()
        except RequestException as err:
            raise MeasurementError('Problems while reading from network') \
                    from err
        except LookupError as err:
            raise MeasurementError('The table has changed') from err

    def read_sensor_data(self):
        """make a network request to the sensortable"""
        url = self.config.get('url')
        url += self.config.get('endpoint')
        _logger.info("Reading data from sensor EconSens3.")
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        _logger.info("Reading of sensor data was successful.")
        self.data = r.text

    def parse(self):
        """parse the data from the request"""
        soup = BeautifulSoup(self.data, 'lxml')

        tables = soup.find_all('table')
        data = EconSens3.parse_table_type_1(tables[0])
        data.update(EconSens3.parse_table_type_2(tables[1]))

        data2 = EconSens3.parse_table_type_1(tables[2])
        for key in data2:
            data[key].update(data2[key])
        return data

    @staticmethod
    def parse_table_type_1(table):
        """tables of type 1 have 1 row with headings and
           in each row one heading and data for the columns of row 1"""

        data = {}
        keys = [th.get_text(strip=True) for th in table.find_all('th')]
        columnkeys, rowkeys = keys[1:-5], keys[-5:]
        rows = [tr for tr in table.find_all('tr')]
        rows.pop(0)  # Remove row with headers
        for i, rkey in enumerate(rowkeys):
            values = [td.get_text(strip=True).replace(',', '.')
                      for td in rows[i].find_all('td')]
            subdata = {}
            for ckey, value in zip(columnkeys, values):
                if value != '':
                    try:
                        subdata[ckey] = float(value)
                    except ValueError:
                        subdata[ckey] = value
            data[rkey] = subdata
        return data

    @staticmethod
    def parse_table_type_2(table):
        """tables of type 2 in each row a key value pair"""

        keys = [th.get_text(strip=True) for th in table.find_all('th')]
        values = [float(td.get_text(strip=True).replace(',', '.'))
                  for td in table.find_all('td')]
        return dict(zip(keys, values))
# vim: ft=python ts=4 sta sw=4 et ai
# python: 3
