from Queue import Queue
from podcasts.site_crawler import SiteCrawler
from podcasts.series_worker import SeriesWorker

class SeriesDriver(object):
  """
  Drives the acquisition of series +
  their subsequent storage in `directory`
  """

  def __init__(self, directory, num_threads=10):
    self.directory = directory
    self.num_threads = num_threads

  def get_series_from_urls(self, urls):
    genre_urls = Queue(len(urls))
    for u in urls:
      genre_urls.put(u)

    for _ in xrange(0, self.num_threads):
      t = SeriesWorker(self.directory, genre_urls)
      t.daemon = True
      t.start()

    genre_urls.join()
