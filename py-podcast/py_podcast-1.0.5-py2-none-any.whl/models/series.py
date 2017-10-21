import json
from podcasts.models.entity import Entity

class Series(Entity):
  # Static (class variable, access via Series.fields)
  fields = [
      'id',
      'title',
      'country',
      'author',
      'image_url_sm',
      'image_url_lg',
      'feed_url',
      'genres',
      'description'
  ]

  def __init__(self, **kwargs):
    self.type = 'series'
    self.id = kwargs.get('s_id')
    self.title = kwargs.get('title').encode('utf-8')
    self.country = kwargs.get('country').encode('utf-8')
    self.author = kwargs.get('author').encode('utf-8')
    self.image_url_sm = kwargs.get('image_url_sm').encode('utf-8')
    self.image_url_lg = kwargs.get('image_url_lg').encode('utf-8')
    self.feed_url = kwargs.get('feed_url').encode('utf-8')
    self.genres = kwargs.get('genres').encode('utf-8')
    self.description = None

  def set_description(self, description):
    self.description = description

  def __hash__(self):
    return self.id # unique per series

  @classmethod
  def from_itunes_json(cls, J):
    return cls(
        s_id=J['collectionId'],
        title=J['collectionName'],
        country=J['country'],
        author=J['artistName'],
        image_url_sm=J['artworkUrl60'],
        image_url_lg=J['artworkUrl600'],
        feed_url=J['feedUrl'],
        genres=';'.join(J['genres'])
    )

  @classmethod
  def from_db_json(cls, J):
    return cls(
        s_id=J['id'],
        title=J['title'],
        country=J['country'],
        author=J['author'],
        image_url_sm=J['image_url_sm'],
        image_url_lg=J['image_url_lg'],
        feed_url=J['feed_url'],
        genres=';'.join(J['genres'])
    )

  @classmethod
  def from_line(cls, L): # CSV line
    return cls(
        s_id=int(L['id'].decode('utf-8')),
        title=L['title'].decode('utf-8'),
        country=L['country'].decode('utf-8'),
        author=L['author'].decode('utf-8'),
        image_url_sm=L['image_url_sm'].decode('utf-8'),
        image_url_lg=L['image_url_lg'].decode('utf-8'),
        feed_url=L['feed_url'].decode('utf-8'),
        genres=L['genres'].decode('utf-8')
    )

  def to_line(self): # Array in the shape of CSV line
    my_dict = self.__dict__
    return [my_dict[f] for f in Series.fields]
