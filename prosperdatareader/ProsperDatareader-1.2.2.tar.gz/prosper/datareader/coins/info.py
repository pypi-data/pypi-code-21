"""datareader.coins.info.py: tools for fetching cryptocoin metadata"""
from datetime import datetime
import itertools
from os import path
from enum import Enum

import requests
import pandas as pd

from .. import config
from .. import exceptions
#from prosper.datareader.config import LOGGER as G_LOGGER
#import prosper.datareader.exceptions as exceptions

LOGGER = config.LOGGER
HERE = path.abspath(path.dirname(__file__))

__all__ = (
    'get_symbol_hitbtc', 'get_ticker_info', 'supported_symbol_info'
)

class Sources(Enum):
    hitbtc = 'hitbtc'
    cc = 'cryptocompare'

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

################################################################################

def supported_symbol_info(
        key_name,
        source=Sources.hitbtc
):
    """find unique values for key_name in symbol feed

    Args:
        key_name (str): name of key to search
        source (:obj:`Enum`): source name

    Returns:
        (:obj:`list`): list of unique values

    """
    if isinstance(source, str):
        source = Sources(source)

    if source == Sources.hitbtc:
        symbols_df = pd.DataFrame(get_supported_symbols_hitbtc())
    elif source == Sources.cc:
        symbols_df = pd.DataFrame(get_supported_symbols_cc())
    else:  # pragma: no cover
        raise exceptions.UnsupportedSource()

    unique_list = list(symbols_df[key_name].unique())

    return unique_list

def get_symbol_hitbtc(
        commodity_ticker,
        currency_ticker,
        logger=LOGGER
):
    """get valid ticker to look up

    Args:
        commodity_ticker (str): short-name for crypto coin
        currency_ticker (str): short-name for currency
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (str): valid ticker for HITBTC

    """
    logger.info('--Fetching symbol list from API')
    symbols_df = pd.DataFrame(get_supported_symbols_hitbtc())

    symbol = symbols_df.query(
        'commodity==\'{commodity}\' & currency==\'{currency}\''.format(
            commodity=commodity_ticker.upper(),
            currency=currency_ticker.upper()
        ))

    if symbol.empty:
        raise exceptions.SymbolNotSupported()

    return symbol['symbol'].iloc[0]

def get_ticker_info(
        ticker,
        logger=LOGGER
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
