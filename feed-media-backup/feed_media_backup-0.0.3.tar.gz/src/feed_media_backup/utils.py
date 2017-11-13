"""Utils."""

import os
import sys
from contextlib import contextmanager
from typing import Generator, List

import youtube_dl
from bs4 import BeautifulSoup
from logzero import logger


@contextmanager
def change_dir(directory: str) -> Generator[str, None, None]:
    """Contextmanager to temporary change working directory."""
    cwd = os.path.abspath(os.getcwd())
    os.chdir(os.path.abspath(directory))
    yield os.getcwd()
    os.chdir(cwd)


def get_urls(html: str) -> List[str]:
    """Extract urls from html."""
    soup = BeautifulSoup(html, 'lxml')

    urls = [a['href'] for a in soup.find_all('a')]
    logger.debug('found %s', ' '.join(urls))

    return urls


def download(url: str, dest: str) -> bool:
    """Download media from url."""
    # youtube-dl options
    ydl_opts = {
        'logger': logger,
    }
    with change_dir(dest):

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return True

        except youtube_dl.utils.DownloadError:
            logger.error('Could not find media')

            return False

        except KeyboardInterrupt:
            sys.exit()

        except BaseException as error:
            logger.exception(str(error))
            return False
