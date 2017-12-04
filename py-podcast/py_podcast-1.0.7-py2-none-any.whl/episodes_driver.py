import csv
import os
from Queue import Queue
from podcasts.episode_worker import EpisodeWorker
from podcasts.models.series import Series
from podcasts.models.episode import Episode
from podcasts.storers.json_storer import JsonStorer

class EpisodesDriver(object):
  """
  Drives the acquisition of episodes
  based on series that exist in csv's
  stored in `directory`
  """

  def __init__(self, directory, storer, num_threads=20):
    self.directory = directory
    self.storer = storer
    self.num_threads = num_threads

  def eps_from_series(self):
    """
    Workhorse function that handles grabbing series data from csvs and
    requesting episodal information from RSS feeds
    """
    csvs = []
    for _, _, filenames in os.walk('./{}'.format(self.directory)):
      csvs.extend(filenames)

    series_set = set()
    for c in csvs:
      file_name = './{}/{}'.format(self.directory, c)
      reader = csv.DictReader(open(file_name, 'rb'))
      for line in reader:
        series_set.add(Series.from_line(line))

    series = [s for s in series_set]
    series_q = Queue(len(series))
    for s in series:
      series_q.put(s)

    for _ in xrange(0, self.num_threads):
      t = EpisodeWorker(self.storer, series_q)
      t.daemon = True
      t.start()

    series_q.join()
