#!/usr/bin/env python3
"""EXAMPLE parsers for amazon.com

"""

from webparser.crawler import Crawler

__version__ = r'1.00'
__author__ = r'Mikhail Ananyevskiy (aka soomrack)'


class AmazonBook(Crawler):
    """Parses amazon book webpage.

    Parses:
        + title
        + cover_url
    """

    def __init__(self, url=None):
        self.parsers = {
            self.parse_title,
            self.parse_cover_url
        }
        super().__init__(url)

    def parse_title(self):
        """Parses book title.

        """
        title = self.webdriver.find_element_by_xpath(
            "//span[@id='productTitle'][1]"
        ).get_attribute('innerHTML')
        self.data['title'] = title
        if title:
            return None
        return 'Title not found.'

    def parse_cover_url(self):
        """Parses url of book cover image.

        """
        cover_url = self.webdriver.find_element_by_xpath(
            "//img[@id='imgBlkFront'][1]"
        ).get_attribute('src')
        self.data['cover_url'] = cover_url
        if cover_url:
            return None
        return 'Cover url not found.'


def main():
    print(__doc__)


if __name__ == r'__main__':
    main()
