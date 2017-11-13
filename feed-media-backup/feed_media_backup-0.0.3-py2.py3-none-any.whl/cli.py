"""Cli."""

import logging
import os
from typing import List  # noqa: F401 pylint: disable=unused-import

import click
import feedparser
from logzero import logger, loglevel
from tinydb import Query, TinyDB

from feed_media_backup.utils import download, get_urls


@click.command()
@click.argument(
    'feed'
)
@click.argument(
    'dest',
    type=click.Path(exists=True)
)
@click.option(
    '--force', '-f',
    is_flag=True,
    help='No matter if already worked through feed item.'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='More verbose.'
)
@click.version_option()
def main(feed: str, dest: str, force: bool, verbose: bool) -> None:
    """Backups media from blog RSS feeds."""
    # set log level
    if verbose:
        loglevel(logging.DEBUG)
    else:
        loglevel(logging.INFO)

    # database init
    database = TinyDB(os.path.join(dest, 'db.json'))
    feed_item = Query()

    parsed_feed = feedparser.parse(feed)  # type: feedparser.FeedParserDict
    for entry in parsed_feed['entries']:

        already_in_db = database.search(feed_item.id == entry['id'])

        if not already_in_db or force:

            # getting links
            logger.info('extract links...')

            urls = []  # type: List[str]
            for content in entry.content:
                urls.extend(get_urls(content['value']))

            # try to download links
            logger.info('start to download article media...')
            for url in urls:

                downloaded = download(url, dest)

                if downloaded:
                    logger.info('downloaded %s', url)
                else:
                    logger.info('did not download %s', url)

            # write to db
            if not already_in_db:
                logger.debug('write %s to db...', entry['id'])
                database.insert(
                    {
                        'id': entry['id']
                    }
                )

        else:
            logger.debug('%s already in db', entry['id'])
