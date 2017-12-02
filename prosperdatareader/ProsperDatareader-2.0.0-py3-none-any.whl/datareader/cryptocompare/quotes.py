"""prosper.datareader.cryptocompare.quote: get price data for coins from Cryptocompare"""

import requests

from .. import config
from .. import exceptions

SYMBOLS_URI_CRYPTOCOMPARE = 'https://www.cryptocompare.com/api/data/coinlist/'
def get_supported_symbols_cc(
        uri=SYMBOLS_URI_CRYPTOCOMPARE,
        data_key='Data'
):
    """fetch supported symbols data from API  -- cryptocompare


    Note:
        Supported by cryptocompare
        https://www.cryptocompare.com/api/#-api-data-coinlist-

    Args:
        uri (str, optional): address for API
        data_key (str, optional): data key name in JSON data

    Returns:
        (:obj:`list`): list of supported feeds

    """
    req = requests.get(uri)
    req.raise_for_status()
    data = req.json()

    return list(data[data_key].values())

COIN_TICKER_URI_CC = 'https://min-api.cryptocompare.com/data/pricemultifull'
def get_ticker_cc(
        symbol_list,
        currency='USD',
        price_key='RAW',
        market_list=None,
        uri=COIN_TICKER_URI_CC
):
    """get current price quote from cryptocompare

    Args:
        symbol_list (:obj:`list`): list of coins to look up
        currency (str, optional): which currency to convert to
        price_key (str, optional): which group of data to read (RAW|DISPLAY)
        market_list (:obj:`list`, optional): which market to pull from
        uri (str, optional): resource link

    Returns:
        (:obj:`list`): ticker data for desired coin

    """
    if isinstance(symbol_list, str):
        symbol_list = symbol_list.split(',')

    params = {
        'fsyms': ','.join(symbol_list).upper(),
        'tsyms': currency
    }
    if market_list:
        params['e'] = ','.join(market_list)

    req = requests.get(uri, params=params)
    req.raise_for_status()
    data = req.json()

    if 'Response' in data.keys():
        ## CC returns unique schema in error case ##
        raise exceptions.SymbolNotSupported(data['Message'])

    clean_data = []
    for symbol in symbol_list:
        symbol_row = data[price_key][symbol][currency]
        symbol_row['TICKER'] = symbol + currency
        clean_data.append(symbol_row)

    return clean_data

COIN_HISTO_DAY_URI = 'https://min-api.cryptocompare.com/data/histoday'
def get_histo_day_cc(
        coin,
        limit,
        exchange=None,
        aggregate=None,
        currency='USD',
        data_key='Data',
        uri=COIN_HISTO_DAY_URI
):
    """generate OHLC data for coins

    Notes:
        https://www.cryptocompare.com/api/#-api-data-histoday-

    Args:
        coin (str): short-name of single coin
        limit (int): range to query (max: 2000)
        exchange (str, optional): name of exchange to pull from
        aggregate (int, optional): IDK?
        currenct (str, optional): which currency to convert to FOREX
        data_key (str, optional): name of JSON-key with OHLC data
        uri (str, optional): API endpoint uri

    Returns:
        (:obj:`list`): list of OHLC data

    """
    params = {
        'fsym': coin.upper(),
        'tsym': currency.upper(),
        'limit': int(limit)
    }
    if exchange:
        params['e'] = exchange
    if aggregate:
        params['aggregate'] = aggregate

    req = requests.get(uri, params=params)
    req.raise_for_status()
    data = req.json()

    if data['Response'] == 'Error':
        ## CC returns unique schema in error case ##
        raise exceptions.SymbolNotSupported(data['Message'])

    return data[data_key]
