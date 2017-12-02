"""TMDB api wrapper.
"""

import json
import requests

from datahunters.movies import common


class TMDBAPI(common.MovieAPIBase):
  """Class for TMDB.
  """
  engine = None
  api_key = ""
  root_url = "https://api.themoviedb.org/3/"

  def __init__(self, api_key):
    super(TMDBAPI, self).__init__(api_key)
    with open("configs.json", "r") as f:
      configs = json.load(f)
      self.api_key = configs["api_key"]
    print "TMDB api init"

  def get_movie_info(self, id):
    movie_url = "{}movie/{}?api_key={}&language=en-US".format(self.root_url,
                                                              id, self.api_key)
    res = requests.request("GET", movie_url, data={})
    movie_data = self.convert_to_movieobj(res.json())
    return movie_data

  def map_to_internal_genre(self, genre):
    if genre == "Science Fiction":
      return "Sci-Fi"
    return genre

  def convert_to_movieobj(self, tmdb_movie):
    """Convert TMDB movie object to internal movie object.
    """
    inter_movie = common.MovieObject()
    inter_movie.title = tmdb_movie["title"]
    inter_movie.release_date = tmdb_movie["release_date"]
    inter_movie.imdb_id = tmdb_movie["imdb_id"]
    inter_movie.desc = tmdb_movie["overview"]
    return inter_movie

  def get_person_info(self, id):
    pass


if __name__ == "__main__":
  api = TMDBAPI(None)
  data = api.get_movie_info("10195")
  print data.title