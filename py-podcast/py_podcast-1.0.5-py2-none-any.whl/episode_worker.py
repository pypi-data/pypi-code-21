import os
import pdb
import threading
import podcasts.itunes as itunes
import podcasts.log as log
from podcasts.models.episode import Episode

class EpisodeWorker(threading.Thread):
  def __init__(self, storer, series):
    """
    Constructor for thread that will request the RSS of a
    particular podcast series, parse the series details
    and episode information, and save the information
    w/`storer`
    """
    super(EpisodeWorker, self).__init__()
    self.logger = log.logger
    self.storer = storer
    self.series = series # All series

  def run(self):
    """
    Run the task - compose full series + add to our results
    """
    empty = False
    while not empty:
      try:
        s = self.series.get()
        result_dict = itunes.get_rss_feed_data_from_series(s)
        self.storer.store(result_dict)
        self.logger.info('Retrieved and stored %s', str(s.id))
      except Exception as e: # pylint: disable=W0703
        print e
      finally:
        self.series.task_done()
        empty = self.series.empty()
