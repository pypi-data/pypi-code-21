"""prosper.datareader.hitbtc.quotes: utilities for fetching price/info -- HITBTC"""
import requests
import pandas as pd

from .. import config
from .. import exceptions
#from ..coins import supported_symbol_info

SYMBOLS_URI_HITBTC = 'http://api.hitbtc.com/api/1/public/symbols'
def get_supported_symbols_hitbtc(
        uri=SYMBOLS_URI_HITBTC,
        data_key='symbols'
):
    """fetch supported symbols from API -- hitBTC

    Note:
        Supported by hitbtc
        https://hitbtc.com/api#symbols

    Args:
        uri (str, optional): address for API
        data_key (str, optional): data key name in JSON data

    Returns:
        (:obj:`list`): list of supported feeds

    """
    req = requests.get(uri)
    req.raise_for_status()
    data = req.json()

    return data[data_key]

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
    valid_symbol_list = list(pd.DataFrame(get_supported_symbols_hitbtc())['symbol'].unique())

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
        data = config._listify(data, 'symbol')

    return data

def get_ticker_info_hitbtc(
        ticker,
        logger=config.LOGGER
):
    """reverse lookup, get more info about a requested ticker

    Args:
        ticker (str): info ticker for coin (ex: BTCUSD)
        force_refresh (bool, optional): ignore local cacne and fetch directly from API
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`dict`): hitBTC info about requested ticker

    """
    logger.info('--Fetching symbol list from API')
    data = get_supported_symbols_hitbtc()

    ## Skip pandas, vanilla list search ok here
    for ticker_info in data:
        if ticker_info['symbol'] == ticker.upper():
            return ticker_info

    raise exceptions.TickerNotFound()

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
