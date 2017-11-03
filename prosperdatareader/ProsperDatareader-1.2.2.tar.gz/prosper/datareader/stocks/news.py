"""datareader.stocks.news.py: tools for fetching stock news"""
from datetime import datetime
import itertools
from os import path
import warnings

import demjson
import requests
from six.moves.html_parser import HTMLParser
import pandas as pd

from .. import config
from .. import exceptions

LOGGER = config.LOGGER
HERE = path.abspath(path.dirname(__file__))
#PARSER = HTMLParser()

__all__ = (
    'company_news_google', 'market_news_google', 'company_news_rh'
)

def validate_google_response(response, tag_primary=True):
    """crunches down google response for return

    Args:
        response (:obj:`dict`): data from google response
        tag_primary (bool, optional): certain articles exist at front of lists, mark them

    Returns:
        (:obj:`list`): list of parsed news articles

    """
    article_list = []
    for block in response['clusters']:
        if int(block['id']) == -1:
            continue # final entry is weird

        for index, story in enumerate(block['a']):
            ## Tag primary sources ##
            if index == 0 and tag_primary:
                story['primary'] = True
            elif tag_primary:
                story['primary'] = False

            ## Clean up HTML ##
            story['t'] = HTMLParser().unescape(story['t'])
            story['sp'] = HTMLParser().unescape(story['sp'])

            ## ISO datetime ##
            story['tt'] = datetime.fromtimestamp(int(story['tt'])).isoformat()

            article_list.append(story)

    return article_list

GOOGLE_COMPANY_NEWS = 'https://www.google.com/finance/company_news'
def fetch_company_news_google(
        ticker,
        uri=GOOGLE_COMPANY_NEWS,
        logger=LOGGER
):
    """fetch news for one company ticker

    Args:
        ticker (str): ticker for company
        uri (str, optional): endpoint URI for `company_news`
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`list`): processed news results, JSONable

    """
    logger.info('fetching company_news for %s', ticker)

    params = {
        'q': ticker,
        'output': 'json'
    }
    logger.debug(uri)
    req = requests.get(uri, params=params)
    req.raise_for_status()

    articles_list = []
    try:
        raw_articles = demjson.decode(req.text)
    except Exception as err: #pragma: no cover
        #No coverage: blank news has no single ticker
        logger.debug(req.text)
        if str(err) == 'Can not decode value starting with character \'<\'': #pragma: no cover
            #demjson does not raise unique exceptions :<
            logger.warning('empty news endpoint for %s @ %s', ticker, uri)
            return articles_list
        else:
            logger.error('Unable to parse news items for %s @ %s', ticker, uri, exc_info=True)
            raise err

    logger.info('parsing news object for %s', ticker)
    articles_list = validate_google_response(raw_articles)

    return articles_list

RH_NEWS = 'https://api.robinhood.com/midlands/news/'
PAGE_HARDBREAK = 50
def fetch_company_news_rh(
        ticker,
        page_limit=None,
        uri=RH_NEWS,
        logger=LOGGER
):
    """parse news feed from robhinhood

    Args:
        ticker (str): ticker for desired stock
        page_limit (int, optional): number of pages to fetch to cap results

        uri (str, optional): endpoint address
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`list`): collection of news articles from robinhood

    """
    logger.info('fetching company_news for %s', ticker)
    page = itertools.count(start=1, step=1)

    articles_list = []
    while True:
        ## Generate request ##
        page_num = next(page)

        params = {
            'page': page_num,
            'symbol': ticker.upper()    #caps required
        }
        logger.info('--fetching page %s for %s from %s', page_num, ticker, uri)

        ## GET data ##
        req = requests.get(uri, params=params)
        req.raise_for_status()
        page_data = req.json()

        articles_list.extend(page_data['results'])

        ## Loop or quit ##
        if page_limit and page_num >= page_limit:
            logger.info('--reached page limit: %s:%s', page_num, page_limit)
            break

        if not page_data['next']:
            #NOTE: page_data['next'] does not yield a valid address.  Manually step
            logger.info('--no more pages on endpoint %s', page_num)
            break

        if page_num > PAGE_HARDBREAK:
            warnings.warn(
                'pagination limit {} reached'.format(PAGE_HARDBREAK),
                exceptions.PaginationWarning
            )
            break

    return articles_list

################################################################################

def company_news_google(
        ticker,
        pretty=True,
        _source_override=GOOGLE_COMPANY_NEWS,
        logger=LOGGER
):
    """get news items from Google for a given company

    Args:
        ticker (str): ticker to look up
        pretty (bool, optional): human-readable column names
        keep_google_links (bool, optional): include google metadata links
        _source_override (str, optional): source URI; used to switch feeds
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): tabularized data for news

    """
    logger.info('Fetching company raw data feed for `%s` -- GOOGLE', ticker)
    raw_news_data = fetch_company_news_google(
        ticker,
        uri=_source_override,
        logger=logger
    )

    logger.info('--Pushing data into Pandas')
    news_df = pd.DataFrame(raw_news_data)
    news_df['tt'] = pd.to_datetime(news_df['tt'])

    if pretty:
        logger.info('--Prettifying data')
        col_map = {
            's': 'source',
            'u': 'url',
            't': 'title',
            'sp': 'blurb',
            'tt': 'datetime',
            'd': 'age'
        }
        news_df = news_df.rename(columns=col_map)

    logger.debug(news_df)
    return news_df

GOOGLE_MARKET_NEWS = 'https://www.google.com/finance/market_news'
def market_news_google(
        pretty=True,
        _source_override=GOOGLE_MARKET_NEWS,
        logger=LOGGER
):
    """Get all of today's general finance news from Google

    Args:
        pretty (bool, optional): human-readable column names
        _source_override (str, optional): source URI; used to switch feeds
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`pandas.DataFrame`): tabularized data for news

    """
    logger.info('Fetching general finance news -- GOOGLE')
    news_df = company_news_google(
        '',
        pretty=pretty,
        _source_override=_source_override,
        logger=logger
    )
    logger.debug(news_df)
    return news_df

def company_news_rh(
        ticker,
        page_limit=PAGE_HARDBREAK,
        logger=LOGGER
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
    raw_news_data = fetch_company_news_rh(
        ticker.upper(),
        page_limit=page_limit,
        logger=logger
    )

    logger.info('--Pushing data into Pandas')
    news_df = pd.DataFrame(raw_news_data)
    news_df['published_at'] = pd.to_datetime(news_df['published_at'])

    logger.debug(news_df)
    return news_df
