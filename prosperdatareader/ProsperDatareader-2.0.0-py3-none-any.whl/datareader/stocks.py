"""prosper.datareader.stocks: utilities for looking at stock market data"""

import pandas as pd

import prosper.datareader.robinhood as robinhood  # TODO: simplify import

import prosper.datareader.config as config  # TODO: simplify import

SUMMARY_KEYS = [
    'symbol', 'name', 'pe_ratio', 'change_pct', 'current_price', 'updated_at'
]
def get_quote_rh(
        ticker_list,
        keys=SUMMARY_KEYS,
        logger=config.LOGGER
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
    quotes = robinhood.quotes.fetch_price_quotes_rh(ticker_list, logger=logger)
    for quote in quotes['results']:
        fundamentals = robinhood.quotes.fetch_fundamentals_rh(quote['symbol'], logger=logger)
        instruments = robinhood.quotes.fetch_instruments_rh(quote['instrument'], logger=logger)

        stock_info = {**quote, **fundamentals, **instruments}   #join all data together
        stock_info['is_open'] = robinhood.quotes.market_is_open(instruments['market'])

        if stock_info['is_open']:   #pragma: no cover
            stock_info['current_price'] = stock_info['last_trade_price']
        else:
            stock_info['current_price'] = stock_info['last_extended_hours_trade_price']

        summary_raw_data.append(stock_info)

    summary_df = pd.DataFrame(summary_raw_data)
    summary_df = config._cast_str_to_int(summary_df)

    summary_df['change_pct'] = (summary_df['current_price'] - summary_df['previous_close']) / summary_df['previous_close']

    summary_df['change_pct'] = list(map(
        '{:+.2%}'.format,
        summary_df['change_pct']
    ))
    if keys:
        return summary_df[keys]
    else:
        return summary_df

