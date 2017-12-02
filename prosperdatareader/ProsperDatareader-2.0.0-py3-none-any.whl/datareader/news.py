"""prosper.datareader.news: utilities for looking at news data"""

import pandas as pd

import prosper.datareader.robinhood as robinhood  # TODO: simplify import
import prosper.datareader.exceptions as exceptions
import prosper.datareader.config as config

def company_news_rh(
        ticker,
        page_limit=robinhood.news.PAGE_HARDBREAK,
        logger=config.LOGGER
):
    """get news items from Robinhood for a given company

    Args:
        ticker (str): stock ticker for desired company
        page_limit (int, optional): how many pages to allow in call
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): tabularized data for news

    """
    logger.info('Fetching company raw data feed for `%s` -- ROBINHOOD', ticker)
    raw_news_data = robinhood.news.fetch_company_news_rh(
        ticker.upper(),
        page_limit=page_limit,
        logger=logger
    )

    logger.info('--Pushing data into Pandas')
    news_df = pd.DataFrame(raw_news_data)
    news_df['published_at'] = pd.to_datetime(news_df['published_at'])

    logger.debug(news_df)
    return news_df
