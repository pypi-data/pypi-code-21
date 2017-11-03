"""datareader.stocks.prices.py: tools for fetching stock prices

Meant as companion to: https://pandas-datareader.readthedocs.io/en/latest/
"""
from os import path
from datetime import datetime, timezone
import dateutil.parser

import requests
import pandas as pd

from .. import config

LOGGER = config.LOGGER
HERE = path.abspath(path.dirname(__file__))


__all__ = (
    'get_quote_rh'
)

def cast_str_to_int(dataframe):
    """tries to apply to_numeric to each str column

    Args:
        dataframe (:obj:`pandas.DataFrame`): dataframe to adjust

    Returns:
        (:obj:`pandas.DataFrame`)

    """
    columns = list(dataframe.columns.values)
    for col in columns:
        try:
            dataframe[col] = pd.to_numeric(dataframe[col])
        except Exception:
            pass

    return dataframe

RH_PRICE_QUOTES = 'https://api.robinhood.com/quotes/'
def fetch_price_quotes_rh(
        ticker_list,
        uri=RH_PRICE_QUOTES,
        logger=LOGGER
):
    """fetch quote data from Robinhood

    Notes:
        Currently requires no Auth

    Args:
        ticker_list (:obj:`list` or str): list of tickers to fetch
        uri (str, optional): endpoint URI for `quotes`
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`list`): results from endpoint, JSONable

    """
    ticker_list_str = config._list_to_str(ticker_list)
    logger.info('fetching quote data for %s -- Robinhood', ticker_list_str)

    params = {
        'symbols': ticker_list_str
    }

    req = requests.get(uri, params=params)
    req.raise_for_status()

    data = req.json()
    logger.debug(data)

    return data

RH_FUNDAMENTALS = 'https://api.robinhood.com/fundamentals/'
def fetch_fundamentals_rh(
        ticker,
        uri=RH_FUNDAMENTALS,
        logger=LOGGER
):
    """fetch fundamental data from Robinhood

    Notes:
        Currently requires no Auth

    Args:
        ticker (str): ticker for company
        uri (str, optional): endpoint URI for `fundamentals`
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`dict`): company fundamental data, JSONable

    """
    logger.info('fetching fundamentals data for %s -- Robinhood', ticker)

    fundamental_url = '{uri}{ticker}/'.format(uri=uri, ticker=ticker.upper())
    req = requests.get(fundamental_url)
    req.raise_for_status()

    data = req.json()
    logger.debug(data)

    return data

#RH_INSTRUMENTS = 'https://api.robinhood.com/instruments'
def fetch_instruments_rh(
        instrument_url,
        #uri=RH_INSTRUMENTS,
        logger=LOGGER
):
    """fetch instrument data for stock

    Notes:
        Currently requires no Auth
        company_uid needs to come from another request

    Args:
        company_uid (str): uid for company
        uri (str, optional): endpoint URI for `instruments`
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`dict`): trading data for company, JSONable

    """
    logger.info('fetching instruments data for %s -- Robinhood', instrument_url.split('/')[-1])

    req = requests.get(instrument_url)
    req.raise_for_status()

    data = req.json()
    logger.debug(data)

    return data

def market_is_open(market_uri, logger=LOGGER):
    """checks if market is open right now

    Args:
        market_uri: (str): link to market info
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (bool): https://api.robinhood.com/markets/{market}/hours/{date}/['is_open']

    """
    #TODO: cache me
    #TODO: test me
    market_name = market_uri.split('/')[-1]
    logger.info('fetching market info for %s -- Robinhood', market_name)

    market_req = requests.get(market_uri)
    market_req.raise_for_status()
    market_data = market_req.json()

    logger.info('--checking todays_hours')
    hours_req = requests.get(market_data['todays_hours'])
    hours_req.raise_for_status()
    hours_data = hours_req.json()

    if not hours_data['is_open']:
        return False

    close_datetime = dateutil.parser.parse(hours_data['extended_opens_at'])
    now = datetime.now(timezone.utc)

    if close_datetime > now:
        return False
    else:
        return True

################################################################################

SUMMARY_KEYS = [
    'symbol', 'name', 'pe_ratio', 'change_pct', 'current_price', 'updated_at'
]
def get_quote_rh(
        ticker_list,
        keys=SUMMARY_KEYS,
        logger=LOGGER
):
    """fetch common summary data for stock reporting

    Args:
        ticker_list (:obj:`list`): list of tickers to look up
        keys (:obj:`list`, optional): which keys to present in summary
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): stock info for the day, JSONable
        {'ticker', 'company_name', 'price', 'percent_change', 'PE', 'short_ratio', 'quote_datetime'}

    """
    logger.info('Generating quote for %s -- Robinhood', config._list_to_str(ticker_list))

    ## Gather Required Data ##
    summary_raw_data = []
    quotes = fetch_price_quotes_rh(ticker_list, logger=logger)
    for quote in quotes['results']:
        fundamentals = fetch_fundamentals_rh(quote['symbol'], logger=logger)
        instruments = fetch_instruments_rh(quote['instrument'], logger=logger)

        stock_info = {**quote, **fundamentals, **instruments}   #join all data together
        stock_info['is_open'] = market_is_open(instruments['market'])

        if stock_info['is_open']:   #pragma: no cover
            stock_info['current_price'] = stock_info['last_trade_price']
        else:
            stock_info['current_price'] = stock_info['last_extended_hours_trade_price']

        summary_raw_data.append(stock_info)

    summary_df = pd.DataFrame(summary_raw_data)
    summary_df = cast_str_to_int(summary_df)

    summary_df['change_pct'] = (summary_df['current_price'] - summary_df['previous_close']) / summary_df['previous_close']

    summary_df['change_pct'] = list(map(
        '{:+.2%}'.format,
        summary_df['change_pct']
    ))
    if keys:
        return summary_df[keys]
    else:
        return summary_df
