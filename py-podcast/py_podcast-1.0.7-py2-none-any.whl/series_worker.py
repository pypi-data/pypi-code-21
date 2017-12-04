import os
import time
import threading
import csv
import podcasts.log as log
from podcasts.models.series import Series
from podcasts.series_crawler import SeriesCrawler

class SeriesWorker(threading.Thread):

  def __init__(self, directory, genre_urls):
    super(SeriesWorker, self).__init__()
    self.directory = directory
    self.genre_urls = genre_urls
    self.crawler = SeriesCrawler()
    self.logger = log.logger
    if not os.path.exists('./{}'.format(self.directory)):
      os.makedirs('./{}'.format(self.directory))

  def run(self):
    """
    Requests, parses series, writes to appropriate CSV
    """
    empty = False
    while not empty:
      try:
        # Grab fields
        url = self.genre_urls.get()
        namestamp = "{}.csv".format(str(int(round(time.time() * 1000000))))
        # GET request
        self.logger.info('Attempting to request %s', url)
        self.crawler.set_url(url)
        series = self.crawler.get_series()
        self.logger.info('Attempting to write %s', url)
        # Grab writer -> writes series
        csv_dir = './{}/{}'.format(self.directory, namestamp)
        writer = csv.writer(open(csv_dir, 'wb'))
        writer.writerow(Series.fields)
        for s in series:
          writer.writerow(s.to_line())
        self.logger.info('Wrote %s', namestamp)
      except Exception, e: # pylint: disable=W0703
        print e
      finally:
        self.genre_urls.task_done()
        empty = self.genre_urls.empty()
