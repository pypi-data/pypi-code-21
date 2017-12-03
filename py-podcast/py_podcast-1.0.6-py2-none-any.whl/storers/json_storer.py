import os
import json
from podcasts.storers.storer import Storer

class JsonStorer(Storer):
  """
  Storer of podcasts in JSON form
  """

  def __init__(self, directory):
    self.directory = directory
    if not os.path.exists('./{}'.format(self.directory)):
      os.makedirs('./{}'.format(self.directory))

  def store(self, result_dict):
    s_id = result_dict['series']['id']
    dir_path = './{}/{}.json'.format(self.directory, str(s_id))
    with open(dir_path, 'wb') as outfile:
      json.dump(result_dict, outfile)
