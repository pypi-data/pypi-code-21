""" Utility for related items
"""
from urllib2 import urlparse
from bs4 import BeautifulSoup
from zope.interface import implements
from eea.alchemy.interfaces import IDiscoverLinks

class DiscoverLinks(object):
    """ Discover internal links
    """
    implements(IDiscoverLinks)

    def __call__(self, text="", match=""):
        match = match.replace('https://', 'http://')
        soup = BeautifulSoup(text)

        items = set()
        for link in soup.find_all('a'):
            href = link.get('href')
            if href is None:
                continue
            href = href.replace('https://', 'http://')

            ourl = urlparse.urlparse(href)
            ourl = ourl._replace(fragment='', query='', params='')
            href = ourl.geturl()

            if u'resolveuid' in href:
                items.add(href)
            elif href.startswith('../'):
                items.add(href)
            elif match and href.startswith(match):
                found = href[len(match):]
                found = found.strip('/')
                items.add(found)
            elif href.startswith('/'):
                href = href.strip('/')
                items.add(href)

        for link in items:
            yield {
                'count': 1,
                'type': 'Link',
                'text': link,
                'relevance': '100.0'
            }
