"""prosper.datareader.coins: utilities for looking up info on cryptocoins"""
from enum import Enum

import pandas as pd

# TODO: Simplify import #
import prosper.datareader.config as config
import prosper.datareader.exceptions as exceptions
import prosper.datareader.cryptocompare as cryptocompare
import prosper.datareader.hitbtc as hitbtc

class Sources(Enum):
    hitbtc = 'hitbtc'
    cc = 'cryptocompare'

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
    if source == Sources.hitbtc:
        index_key = 'symbol'
        quote_df = quote_df.rename(index=quote_df[index_key])

    elif source == Sources.cc:
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
        symbols_df = pd.DataFrame(hitbtc.quotes.get_supported_symbols_hitbtc())
    elif source == Sources.cc:
        symbols_df = pd.DataFrame(cryptocompare.quotes.get_supported_symbols_cc())
    else:  # pragma: no cover
        raise exceptions.UnsupportedSource()

    unique_list = list(symbols_df[key_name].unique())

    return unique_list

def get_symbol_hitbtc(
        commodity_ticker,
        currency_ticker,
        logger=config.LOGGER
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
    symbols_df = pd.DataFrame(hitbtc.quotes.get_supported_symbols_hitbtc())

    symbol = symbols_df.query(
        'commodity==\'{commodity}\' & currency==\'{currency}\''.format(
            commodity=commodity_ticker.upper(),
            currency=currency_ticker.upper()
        ))

    if symbol.empty:
        raise exceptions.SymbolNotSupported()

    return symbol['symbol'].iloc[0]

def get_quote_hitbtc(
        coin_list,
        currency='USD',
        to_yahoo=False,
        logger=config.LOGGER
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
    ticker_list = hitbtc.quotes.coin_list_to_symbol_list(
        coin_list,
        currency=currency,
        strict=True
    )

    logger.info('--fetching ticker data')
    raw_quote = hitbtc.quotes.get_ticker_hitbtc('')
    quote_df = pd.DataFrame(raw_quote)
    if to_yahoo:
        logger.info('--converting column names to yahoo style')
        quote_df = columns_to_yahoo(quote_df, Sources.hitbtc)

    logger.info('--filtering ticker data')
    quote_df = quote_df[quote_df['symbol'].isin(ticker_list)]
    quote_df = quote_df[list(quote_df.columns.values)].apply(pd.to_numeric, errors='ignore')
    quote_df['change_pct'] = (quote_df['last'] - quote_df['open']) / quote_df['open'] * 100

    logger.debug(quote_df)
    return quote_df

def get_orderbook_hitbtc(
        coin,
        which_book,
        currency='USD',
        logger=config.LOGGER
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
    symbol = hitbtc.quotes.coin_list_to_symbol_list(
        [coin],
        currency=currency,
        strict=True
    )[0]

    logger.info('--fetching orderbook')
    raw_orderbook = hitbtc.quotes.get_order_book_hitbtc(symbol)[which_book]

    orderbook_df = pd.DataFrame(raw_orderbook, columns=['price', 'ammount'])
    orderbook_df['symbol'] = symbol
    orderbook_df['coin'] = coin
    orderbook_df['orderbook'] = which_book

    logger.debug(orderbook_df)
    return orderbook_df

def get_quote_cc(
        coin_list,
        currency='USD',
        coin_info_df=None,
        to_yahoo=False,
        logger=config.LOGGER
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

    # TODO: only fetch symbol list when required?
    if coin_info_df is None:
        logger.info('--Gathering coin info')
        coin_info_df = pd.DataFrame(cryptocompare.quotes.get_supported_symbols_cc())
    else:
        # make sure expected data is in there
        headers = list(coin_info_df.columns.values)
        assert 'Name' in headers   # avoid merge issue


    logger.info('--Fetching ticker data')
    ticker_df = pd.DataFrame(cryptocompare.quotes.get_ticker_cc(coin_list, currency=currency))

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
            Sources.cc
        )

    quote_df = quote_df[list(quote_df.columns.values)].apply(pd.to_numeric, errors='ignore')
    logger.debug(quote_df)
    return quote_df

def get_ohlc_cc(
        coin,
        limit,
        currency='USD',
        frequency=OHLCfrequency.day,
        logger=config.LOGGER
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
    data = cryptocompare.quotes.get_histo_day_cc(
        coin,
        limit,
        currency=currency,
        uri=frequency.address()
    )

    ohlc_df = pd.DataFrame(data)
    ohlc_df['datetime'] = pd.to_datetime(ohlc_df['time'], unit='s')

    return ohlc_df
