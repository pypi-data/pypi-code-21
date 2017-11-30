"""prosper.datareader.robinhood.news: news parsing from Robinhood"""
import itertools
import warnings

import requests

from .. import config
from .. import exceptions

RH_NEWS = 'https://api.robinhood.com/midlands/news/'
PAGE_HARDBREAK = 50
def fetch_company_news_rh(
        ticker,
        page_limit=None,
        uri=RH_NEWS,
        _page_hardbreak=PAGE_HARDBREAK,  # FIXME?: does this need to move?
        logger=config.LOGGER
):
    """parse news feed from robhinhood

    Args:
        ticker (str): ticker for desired stock
        page_limit (int, optional): number of pages to fetch to cap results
        uri (str, optional): endpoint address
        _page_hardbreak (int, optional): error level for hard-capping limits
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

        if page_num > _page_hardbreak:
            warnings.warn(
                'pagination limit {} reached'.format(PAGE_HARDBREAK),
                exceptions.PaginationWarning
            )
            break

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



    return articles_list
