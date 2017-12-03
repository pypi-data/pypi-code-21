import urllib
import threading
from copy import deepcopy
from Queue import Queue
import requests
import feedparser
from podcasts.constants import ITUNES_SEARCH_URL, ITUNES_LOOKUP_URL
from podcasts.api import API
from podcasts.models.series import Series
from podcasts.models.episode import Episode

def search_podcast_series(query):
  params = {'entity': 'podcast', 'limit': 20, 'term': query}
  encoded_params = urllib.urlencode(params)
  results = API().\
    req_itunes(ITUNES_SEARCH_URL + encoded_params).\
    json()['results']
  return [
      Series.from_itunes_json(j) for j in results
      if j.get('feedUrl') is not None]

def get_series_by_ids(ids):
    ids_with_coms = ','.join(ids)
    id_param = {'id': ids_with_coms}
    results = API().\
      req_itunes(ITUNES_LOOKUP_URL + urllib.urlencode(id_param)).\
      json()['results']
    return [
        Series.from_itunes_json(j) for j in results
        if j.get('feedUrl') is not None]

def get_rss_feed_data_from_series(s):
  # Grab full RSS feed
  rss = feedparser.parse(s.feed_url)
  # Grab all episodes from the RSS feed
  ep_dicts = [Episode(s, entry).__dict__ for entry in rss.get('entries', [])]
  description = rss.get('feed', dict()).get('summary', '')
  s.set_description(description)
  # Build up resultant dictionary
  result_dict = dict()
  result_dict['series'] = deepcopy(s.__dict__)
  result_dict['series']['genres'] = result_dict['series']['genres'].split(';')
  result_dict['episodes'] = ep_dicts
  return result_dict

def get_feeds_from_many_series(many_series):
  # Global data-structures available to all threads
  result_buffer = []
  q = Queue(len(many_series))
  # The function each thread runs over and over
  # to grab all episodes given many series, each
  # with a feed_url
  def grab_feeds():
    empty = False
    while not empty:
      try:
        s = q.get()
        result_buffer.append(get_rss_feed_data_from_series(s))
      except Exception as e: # pylint: disable=W0703
        print e
      finally:
        q.task_done()
        empty = q.empty()
  # Populate the queue with series, run threads, and
  # return results
  for s in many_series:
    q.put(s)
  for _ in xrange(0, 25):
    t = threading.Thread(target=grab_feeds)
    t.daemon = True
    t.start()
  q.join()
  return result_buffer
