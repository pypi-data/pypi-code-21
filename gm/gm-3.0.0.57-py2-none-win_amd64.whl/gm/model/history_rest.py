from __future__ import print_function, absolute_import, unicode_literals

import datetime
import requests
import pandas as pd

from gm.constant import HISTORY_REST_ADDR
from gm.csdk.c_sdk import py_gmi_get_serv_addr
from gm.utils import ObjectLikeDict


class HistoryRestApi(object):
    HISTORY_TICKS_URL = '/v3/data-history/ticks'
    HISTORY_BARS_URL = '/v3/data-history/bars'
    HISTORY_N_TICKS_URL = '/v3/data-history/ticks-n'
    HISTORY_N_BARS_URL = '/v3/data-history/bars-n'

    def __init__(self):
        addr = (py_gmi_get_serv_addr(HISTORY_REST_ADDR))
        if isinstance(addr, bytes):
            addr = bytes.decode(addr)
        self.base_url = 'http://{}'.format(addr)

    def get_history_bars(self, symbols, frequency, start_time, end_time, fields=None,
                         skip_suspended=True, fill_missing=None, adjust='pre', df=False):

        data = {'symbols': symbols,
                'frequency': frequency,
                'start_time': start_time,
                'end_time': end_time,
                'fields': fields,
                'skip_suspended': skip_suspended,
                'fill_missing': fill_missing,
                'adjust': adjust
                }

        try:
            url = self.base_url + HistoryRestApi.HISTORY_BARS_URL
            data = requests.get(url, params=data)
            status = data.status_code
            data = data.json()
            if not status == 200:
                return data

            if not data:
                return []

            data = data['data']
            data = self.convert_to_bars(data)
        except Exception as e:
            raise e

        if df:
            return pd.DataFrame(data)

        return [ObjectLikeDict(bar) for bar in data]

    def get_history_ticks(self, symbols, start_time, end_time, fields=None,
                          skip_suspended=True, fill_missing=None, adjust='pre',
                          df=False):

        data = {'symbols': symbols,
                'start_time': start_time,
                'end_time': end_time,
                'fields': fields,
                'skip_suspended': skip_suspended,
                'fill_missing': fill_missing,
                'adjust': adjust
                }

        try:
            url = self.base_url + HistoryRestApi.HISTORY_TICKS_URL
            data = requests.get(url, params=data)
            status = data.status_code
            data = data.json()
            if not status == 200:
                return data

            if not data:
                return []

            data = data['data']
            data = self.convert_to_ticks(data)
        except Exception as e:
            raise e

        if df:
            return pd.DataFrame(data)

        return [ObjectLikeDict(tick) for tick in data]

    def get_history_n_ticks(self, symbol, count, end_time=None, fields=None,
                            skip_suspended=None,
                            fill_missing=None, adjust='pre', df=False):

        data = {'symbol': symbol,
                'count': count,
                'end_time': end_time,
                'fields': fields,
                'skip_suspended': skip_suspended,
                'fill_missing': fill_missing,
                'adjust': adjust}

        try:
            url = self.base_url + HistoryRestApi.HISTORY_N_TICKS_URL
            data = requests.get(url, params=data)
            status = data.status_code
            data = data.json()
            if not status == 200:
                return data

            if not data:
                return []

            data = data['data']
            data = self.convert_to_ticks(data)
        except Exception as e:
            raise e

        if df:
            return pd.DataFrame(data)

        return [ObjectLikeDict(tick) for tick in data]

    def get_history_n_bars(self, symbol, frequency, count, end_time=None,
                           fields=None, skip_suspended=None, fill_missing=None,
                           adjust='pre', df=False):

        data = {'symbol': symbol,
                'frequency': frequency,
                'count': count,
                'end_time': end_time,
                'fields': fields,
                'skip_suspended': skip_suspended,
                'fill_missing': fill_missing,
                'adjust': adjust}

        try:
            url = self.base_url + HistoryRestApi.HISTORY_N_BARS_URL
            data = requests.get(url, params=data)
            status = data.status_code
            data = data.json()
            if not status == 200:
                return data

            if not data:
                return []

            data = data['data']
            data = self.convert_to_bars(data)
        except Exception as e:
            raise e

        if df:
            return pd.DataFrame(data)

        return [ObjectLikeDict(bar) for bar in data]

    @staticmethod
    def convert_to_bars(data):
        for info in data:
            if info.get('eob'):
                info['eob'] = datetime.datetime.strptime(info['eob'], '%Y-%m-%dT%H:%M:%S')
            if info.get('bob'):
                info['bob'] = datetime.datetime.strptime(info['bob'], '%Y-%m-%dT%H:%M:%S')
        return data

    @staticmethod
    def convert_to_ticks(data):
        for info in data:
            if info.get('created_at'):
                info['created_at'] = datetime.datetime.strptime(info['created_at'],'%Y-%m-%dT%H:%M:%S')
        return data



if __name__ == '__main__':
    a = HistoryRestApi()
    print (a.get_history_ticks(symbols='SHSE.600000', start_time='2017-08-17', end_time='2017-08-21', fields='symbol', df=True))
    print (a.get_history_bars(symbols='SHSE.600000', frequency='1d', start_time='2017-08-17', end_time='2017-08-21', fields='symbol', df=True))
    print (a.get_history_n_bars(symbol='SHSE.600000', frequency='1d', count=5, end_time='2017-08-21', fields='symbol', df=True))
    print (a.get_history_n_ticks(symbol='SHSE.600000',  count=5, end_time='2017-08-21', fields='symbol', df=True))