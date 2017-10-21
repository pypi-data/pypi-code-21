import string
import requests as r
from lxml import html
import podcasts.log as log
from podcasts.series_crawler import SeriesCrawler
from podcasts.constants import ITUNES_GENRES_URL

# Entity with utilities for iTunes preview site for Podcasts
class SiteCrawler(object):

  def __init__(self):
    self.logger = log.logger

  def get_genres(self):
    """
    Grab genre URLs from iTunes Podcast preview
    """
    page = r.get(ITUNES_GENRES_URL)
    tree = html.fromstring(page.content)
    elements = tree.xpath("//a[@class='top-level-genre']")
    return [e.attrib['href'] for e in elements]

  def generate_urls_for_genre(self, genre_url):
    """
    Generate URL's for genre
    """
    letters = list(string.ascii_uppercase)
    urls = []
    for letter in letters:
      base = '{}&letter={}'.format(genre_url, letter)
      page = r.get(base)
      tree = html.fromstring(page.content)
      elements = tree.xpath("//ul[@class='list paginate']")
      if not elements:
        urls.append(base)
      else:
        for i in xrange(1, self._find_num_pages(base)):
          urls.append('{}&page={}#page'.format(base, i))
    return urls

  def _find_num_pages(self, url):
    """
    Find the number of pages paginating a genre's letter URL
    """
    def _new_url(i):
      return '{}&page={}#page'.format(url, i)
    i = 0
    j = 2000
    k = (i + j) / 2
    crawler = SeriesCrawler(_new_url(k))
    while i < j:
      ids = crawler.get_ids()
      # If we only find one (we've gone too far)
      if len(ids) == 1:
        # Don't decrement by 1 b/c this could be the last page
        j = k
        k = (i + j) / 2
        crawler.set_url(_new_url(k))
      else:
        i = k + 1
        k = (i + j) / 2
        crawler.set_url(_new_url(k))
    return i

  def all_urls(self):
    result = []
    for g_url in self.get_genres():
      self.logger.info('Getting %s', g_url)
      result.extend(self.generate_urls_for_genre(g_url))
    return result
