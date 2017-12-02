from datetime import datetime, timezone
import dateutil.parser

import requests

from .. import config

def market_is_open(market_uri, logger=config.LOGGER):
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


RH_PRICE_QUOTES = 'https://api.robinhood.com/quotes/'
def fetch_price_quotes_rh(
        ticker_list,
        uri=RH_PRICE_QUOTES,
        logger=config.LOGGER
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
        logger=config.LOGGER
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

def fetch_instruments_rh(
        instrument_url,
        logger=config.LOGGER
):
    """fetch instrument data for stock

    Notes:
        Currently requires no Auth
        company_uid needs to come from another request

    Args:
        company_uid (str): uid for company
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
