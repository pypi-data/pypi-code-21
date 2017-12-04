import json
from podcasts.models.entity import Entity

class Episode(Entity):

  def __init__(self, series, entry):
    self.type = 'episode'
    self.series_id = series.id
    self.series_title = series.title # Already encoded
    self.image_url_sm = series.image_url_sm # Already encoded
    self.image_url_lg = series.image_url_lg # Already encoded
    self.title = entry.get('title', '').encode('utf-8')
    self.author = entry.get('author', '').encode('utf-8')
    self.summary = entry.\
        get('summary_detail', {}).\
        get('value', '').\
        encode('utf-8')
    self.pub_date = self._build_date(entry.get('published_parsed', None))
    self.duration = entry.get('itunes_duration', '').encode('utf-8')
    self.tags = [
        (t['term'] if t['term'] is None else t['term'].encode('utf-8'))
        for t in entry.get('tags', [])]

    self.audio_url = None
    for l in entry.get('links', []):
      if ('type' in l) \
      and ('href' in l) \
      and ('type' in l) \
      and ('audio' in l['type']):
        self.audio_url = l['href'].encode('utf-8')
        break
