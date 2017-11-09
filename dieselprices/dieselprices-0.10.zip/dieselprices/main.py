import requests
import json
import os
from collections import namedtuple
from datetime import datetime, timedelta

PricesByWeek = namedtuple('PricesByWeek', 'week price')

class MissingKeyError(Exception):
    ''' Exception for bad key '''
    def __init__(self):
        super().__init__('Key is incorrect or missing')


class RetrievalError(Exception):
    '''Catch all exception if there is an error in json result'''
    def __init__(self):
        super().__init__('Error retrieving data')

def key(api_key=None):
    """Save API Key or return it"""
    if 'KEY' not in os.environ.keys():
        os.environ['KEY'] = api_key
    else:
        return os.getenv('KEY')


def get_data(url):
    """get json from eia site"""
    data = json.loads(requests.get(url).text)
    if 'missing api_key' in str(data):
        raise MissingKeyError
    elif 'error' in str(data):
        raise RetrievalError
    return data


def to_int(data):
    """convert string or list to int"""
    if not data:
        return None
    elif type(data) == list:
        return [int(item) for item in data]
    else:
        return int(data)


class Prices:
    """
        class returns price for week, weeks or current week
        if no arguments passed then current week data is returned
        if week argument is passed then price is returned for that week
        if weeks argument is passed then a list of tuples is returned with weeks and prices
        if weeks and weeks are passed then only week is returned
    """
    def __init__(self, week=None, weeks=None):
        """initialize the Prices class"""
        self.url = 'http://api.eia.gov/series/?api_key={0}&series_id=PET.EMD_EPD2D_PTE_NUS_DPG.W'.format(key())
        self.week = to_int(week)
        self.weeks = to_int(weeks)
        self.raw_data = get_data(self.url)

    def get_price(self):
        """return the prices or prices from the json data"""
        data = list(self.raw_data['series'][0]['data'])
        price_list = [PricesByWeek(int(week), price) for week, price in data]

        if self.week or (self.week and self.weeks):
            return [item.price for item in price_list if item.week == self.week][0]
        elif self.weeks:
            prices = []
            for week in self.weeks:
                price = [item.price for item in price_list if item.week == week]
                if price:
                    prices.append((week, price[0]))
            return prices
        else:
            monday = datetime.today() - timedelta(days=datetime.today().weekday())
            current_week = int(monday.strftime('%Y%m%d'))
            try:
                return [item.price for item in price_list if item.week == current_week][0]
            except IndexError as e:
                return 'No data yet for current week {0}.'.format(current_week)

