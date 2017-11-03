"""datareader.coins.prices.py: tools for fetching cryptocoin price data"""
from datetime import datetime
from os import path
from enum import Enum

import requests
import pandas as pd

from .. import config
from .. import exceptions
from . import info

LOGGER = config.LOGGER
HERE = path.abspath(path.dirname(__file__))

__all__ = (
    'get_orderbook_hitbtc', 'get_quote_hitbtc', 'get_quote_cc', 'get_ohlc_cc'
)


class OrderBook(Enum):
    """enumerator for handling order book info"""
    asks = 'asks'
    bids = 'bids'

class OHLCfrequency(Enum):
    """enumerator for OHLC scopes"""
    minute = 'minute'
    hour = 'hour'
    day = 'day'

    def address(self):
        """help figure out which address to use"""
        if self == self.minute:
            return 'https://min-api.cryptocompare.com/data/histominute'
        elif self == self.hour:
            return 'https://min-api.cryptocompare.com/data/histohour'
        elif self == self.day:
            return 'https://min-api.cryptocompare.com/data/histoday'
        else:   # pragma: no cover
            raise exceptions.InvalidEnum()

def columns_to_yahoo(
        quote_df,
        source
):
    """recast column names to yahoo equivalent

    Args:
        quote_df (:obj:`pandas.DataFrame`): dataframe to update
        source (:obj:`Enum`): source info

    Returns:
        (:obj:`pandas.DataFrame`): updated dataframe cols

    """
    if source == info.Sources.hitbtc:
        index_key = 'symbol'
        quote_df = quote_df.rename(index=quote_df[index_key])

    elif source == info.Sources.cc:
        ## Remap column names ##
        index_key = 'Name'
        column_map = {
            'CoinName': 'name',
            'FullName': 'more_info',
            'Name': 'symbol',
            'TotalCoinSupply': 'shares_outstanding',
            'TotalCoinsFreeFloat': 'float_shares',
            'LASTVOLUME': 'volume',
            'MKTCAP': 'market_capitalization',
            'CHANGEPCT24HOUR': 'change_pct',
            'MARKET': 'stock_exchange',
            'OPEN24HOUR': 'open',
            'HIGH24HOUR': 'high',
            'LOW24HOUR': 'low',
            'PRICE': 'last',
            'LASTUPDATE': 'timestamp'
        }

        ## Trim unused data ##
        keep_keys = list(column_map.keys())
        keep_keys.append(index_key)
        drop_keys = list(set(list(quote_df.columns.values)) - set(keep_keys))
        quote_df = quote_df.drop(drop_keys, 1)

        ## Apply remap ##
        quote_df = quote_df.rename(
            columns=column_map,
            index=quote_df[index_key])
        quote_df['change_pct'] = quote_df['change_pct'] / 100

    else:  # pragma: no cover
        raise exceptions.UnsupportedSource()

    ## reformat change_pct ##
    quote_df['change_pct'] = list(map(
        '{:+.2%}'.format,
        quote_df['change_pct']
    ))

    ## Timestamp to datetime ##
    quote_df['datetime'] = pd.to_datetime(
        pd.to_numeric(quote_df['timestamp']),
        infer_datetime_format=True,
        #format='%Y-%m-%dT%H:%M:%S',
        errors='coerce'
    )

    return quote_df

def _listify(
        data,
        key_name
):
    """recast data from dict to list, compress keys into sub-dict

    Args:
        data (:obj:`dict`): data to transform (dict(dict))
        key_name (str): name to recast key to

    Returns:
        (:obj:`list`): fixed data

    """
    listified_data = []
    for key, value in data.items():
        row = dict(value)
        row[key_name] = key
        listified_data.append(row)

    return listified_data

def coin_list_to_symbol_list(
        coin_list,
        currency='USD',
        strict=False
):
    """convert list of crypto currencies to HitBTC symbols

    Args:
        coin_list (str or :obj:`list`): list of coins to convert
        currency (str, optional): currency to FOREX against
        strict (bool, optional): throw if unsupported ticker is requested

    Returns:
        (:obj:`list`): list of valid coins and tickers

    """
    valid_symbol_list = info.supported_symbol_info('symbol')

    symbols_list = []
    invalid_symbols = []
    for coin in coin_list:
        ticker = str(coin).upper() + currency
        if ticker not in valid_symbol_list:
            invalid_symbols.append(ticker)

        symbols_list.append(ticker)

    if invalid_symbols and strict:
        raise KeyError('Unsupported ticker requested: {}'.format(invalid_symbols))

    return symbols_list

COIN_TICKER_URI_HITBTC = 'http://api.hitbtc.com/api/1/public/{symbol}/ticker'
def get_ticker_hitbtc(
        symbol,
        uri=COIN_TICKER_URI_HITBTC
):
    """fetch quote for coin

    Notes:
        incurs a .format(ticker=symbol) call, be careful with overriding uri

    Args:
        symbol (str): name of coin-ticker to pull
        uri (str, optional): resource link

    Returns:
        (:obj:`dict`) or (:obj:`list`): ticker data for desired coin

    """
    full_uri = ''
    if not symbol:
        ## fetching entire ticker list ##
        full_uri = uri.replace(r'{symbol}/', '')
    else:
        full_uri = uri.format(symbol=symbol)

    req = requests.get(full_uri)
    req.raise_for_status()
    data = req.json()

    if not symbol:
        ## fetching entire ticker list ##
        data = _listify(data, 'symbol')

    return data

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

COIN_ORDER_BOOK_URI = 'http://api.hitbtc.com/api/1/public/{symbol}/orderbook'
def get_order_book_hitbtc(
        symbol,
        format_price='number',
        format_amount='number',
        uri=COIN_ORDER_BOOK_URI
):
    """fetch orderbook data

    Notes:
        incurs a .format(ticker=symbol) call, be careful with overriding uri

    Args:
        symbol (str): name of coin-ticker to pull
        format_price (str, optional): optional format helper
        format_amount (str, optional): optional format helper
        uri (str, optional): resource link

    Returns:
        (:obj:`dict`): order book for coin-ticker

    """
    params = {}
    #TODO: this sucks
    if format_price:
        params['format_price'] = format_price
    if format_amount:
        params['format_amount'] = format_amount

    full_uri = uri.format(symbol=symbol)
    req = requests.get(full_uri, params=params)
    req.raise_for_status()

    data = req.json()

    return data #return both bids/asks for other steps to clean up later

################################################################################

def get_quote_hitbtc(
        coin_list,
        currency='USD',
        to_yahoo=False,
        logger=LOGGER
):
    """fetch common summary data for crypto-coins

    Args:
        coin_list (:obj:`list`): list of tickers to look up'
        currency (str, optional): currency to FOREX against
        to_yahoo (bool, optional): convert names to yahoo analog
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): coin info for the day, JSONable

    """
    logger.info('Generating quote for %s -- HitBTC', config._list_to_str(coin_list))

    logger.info('--validating coin_list')
    ticker_list = coin_list_to_symbol_list(
        coin_list,
        currency=currency,
        strict=True
    )

    logger.info('--fetching ticker data')
    raw_quote = get_ticker_hitbtc('')
    quote_df = pd.DataFrame(raw_quote)
    if to_yahoo:
        logger.info('--converting column names to yahoo style')
        quote_df = columns_to_yahoo(quote_df, info.Sources.hitbtc)

    logger.info('--filtering ticker data')
    quote_df = quote_df[quote_df['symbol'].isin(ticker_list)]
    quote_df = quote_df[list(quote_df.columns.values)].apply(pd.to_numeric, errors='ignore')
    quote_df['change_pct'] = (quote_df['last'] - quote_df['open']) / quote_df['open'] * 100

    logger.debug(quote_df)
    return quote_df

def get_quote_cc(
        coin_list,
        currency='USD',
        coin_info_df=None,
        to_yahoo=False,
        logger=LOGGER
):
    """fetch common summary data for crypto-coins

    Args:
        coin_list (:obj:`list`): list of tickers to look up'
        currency (str, optional): currency to FOREX against
        coin_info_df (:obj:`pandas.DataFrame`, optional): coin info (for caching)
        to_yahoo (bool, optional): convert names to yahoo analog
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): coin info for the day, JSONable

    """
    logger.info('Generating quote for %s -- CryptoCompare', config._list_to_str(coin_list))

    #TODO: only fetch symbol list when required?
    if coin_info_df is None:
        logger.info('--Gathering coin info')
        coin_info_df = pd.DataFrame(info.get_supported_symbols_cc())
    else:
        #make sure expected data is in there
        headers = list(coin_info_df.columns.values)
        assert 'Name' in headers   # avoid merge issue


    logger.info('--Fetching ticker data')
    ticker_df = pd.DataFrame(get_ticker_cc(coin_list, currency=currency))

    logger.info('--combining dataframes')
    quote_df = pd.merge(
        ticker_df, coin_info_df,
        how='inner',
        left_on='FROMSYMBOL',
        right_on='Name'
    )

    if to_yahoo:
        logger.info('--converting headers to yahoo format')
        quote_df = columns_to_yahoo(
            quote_df,
            info.Sources.cc
        )

    quote_df = quote_df[list(quote_df.columns.values)].apply(pd.to_numeric, errors='ignore')
    logger.debug(quote_df)
    return quote_df

def get_ohlc_cc(
        coin,
        limit,
        currency='USD',
        frequency=OHLCfrequency.day,
        logger=LOGGER
):
    """gather OHLC data for given coin

    Args:
        coin (str): name of coin to look up
        limit (int): total range for OHLC data (max 2000)
        currency (str, optional): currency to compare coin to
        frequency (:obj;`Enum`, optional): which range to use (minute, hour, day)
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): OHLC data

    """
    if isinstance(frequency, str):
        frequency = OHLCfrequency(frequency)

    logger.info('Fetching OHLC data @%s for %s -- CryptoCompare', frequency.value, coin)
    data = get_histo_day_cc(
        coin,
        limit,
        currency=currency,
        uri=frequency.address()
    )

    ohlc_df = pd.DataFrame(data)
    ohlc_df['datetime'] = pd.to_datetime(ohlc_df['time'], unit='s')

    return ohlc_df

def get_orderbook_hitbtc(
        coin,
        which_book,
        currency='USD',
        logger=LOGGER
):
    """fetch current orderbook from hitBTC

    Args:
        coin (str): name of coin to fetch
        which_book (str): Enum, 'asks' or 'bids'
        currency (str, optional): currency to FOREX against

    logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): current coin order book

    """
    logger.info('Generating orderbook for %s -- HitBTC', coin)
    order_enum = OrderBook(which_book)  # validates which order book key to use

    logger.info('--validating coin')
    symbol = coin_list_to_symbol_list(
        [coin],
        currency=currency,
        strict=True
    )[0]

    logger.info('--fetching orderbook')
    raw_orderbook = get_order_book_hitbtc(symbol)[which_book]

    orderbook_df = pd.DataFrame(raw_orderbook, columns=['price', 'ammount'])
    orderbook_df['symbol'] = symbol
    orderbook_df['coin'] = coin
    orderbook_df['orderbook'] = which_book

    logger.debug(orderbook_df)
    return orderbook_df
