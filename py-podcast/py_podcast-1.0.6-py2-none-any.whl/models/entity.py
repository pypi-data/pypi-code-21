import json
from datetime import datetime

class Entity(object):
  """
  Parent of all models of this driver
  """

  def to_json(self):
    return json.dumps(self.__dict__, default=json_serial)

  def _build_date(self, d):
    if d is not None:
      dt = datetime(d.tm_year, d.tm_mon, d.tm_mday,
                    d.tm_hour, d.tm_min, d.tm_sec)
      print dt
      # Unix timestamp
      return int((dt - datetime(1970, 1, 1)).total_seconds())
    return None
