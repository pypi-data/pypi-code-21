import requests
from lxml import html
from podcasts.itunes import get_series_by_ids

# SeriesCrawler, to get series from a particular webpage
class SeriesCrawler(object):

  def __init__(self, url=''):
    self.url = url
    self.ids = []

  def set_url(self, url):
    self.url = url

  def _e_to_id(self, e): # href element to series_id
    return e.attrib['href'][(e.attrib['href'].\
      rfind('/id')+3):].\
      replace('?mt=2', '')

  def get_ids(self):
    page = requests.get(self.url)
    tree = html.fromstring(page.content)
    ids_elements = tree.xpath("//div[@id='selectedcontent']/div/ul/li/a")
    return [self._e_to_id(e) for e in ids_elements]

  def get_series(self):
    ids = self.get_ids()
    i = 0
    j = 100
    series = []
    while i < len(ids):
      curr_ids = ids[i:j]
      results = get_series_by_ids(curr_ids)
      series.extend(results)
      i += 100
      j += 100

    return series
