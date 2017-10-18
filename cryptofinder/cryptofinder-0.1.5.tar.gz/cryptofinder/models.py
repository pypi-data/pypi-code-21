from .config import DBFILE, APP_ENV
import datetime
from peewee import *

if APP_ENV == 'development':
  db = PostgresqlDatabase('cryptofinder', user='postgres', password='password', host='localhost')
else:
  db = SqliteDatabase(DBFILE)

class Base(Model):
  class Meta:
    database = db

  def __str__(self):
    attrs = {}
    for k in self._data.keys():
      try:
        attrs[k] = str(getattr(self, k))
      except:
        attrs[k] = json.dumps(getattr(self, k))
    return str(attrs)

  @property
  def props(self):
    props = {}
    for k in self._data.keys():
      try:
        props[k] = str(getattr(self, k))
      except:
        props[k] = json.dumps(getattr(self, k))
    return props

class Coin(Base):
  slug = TextField()
  name = TextField(default='', null=True)
  symbol = TextField(default='', null=True)
  rank = IntegerField(default=0, null=True)
  last_updated = DateTimeField(default=datetime.datetime.now, null=True)
  avail_supply = FloatField(default=0.0, null=True)
  avail_supply_ratio = FloatField(default=0.0, null=True)
  day_volume_ratio = FloatField(default=0.0, null=True)
  day_volume = FloatField(default=0.0, null=True)
  market_cap = FloatField(default=0.0, null=True)
  percent_change_1h = FloatField(default=0.0, null=True)
  percent_change_24h = FloatField(default=0.0, null=True)
  percent_change_7d = FloatField(default=0.0, null=True)
  price_btc = FloatField(default=0.0, null=True)
  price_usd = FloatField(default=0.0, null=True)
  total_supply = FloatField(default=0.0, null=True)

class Database:
  @classmethod
  def connect(self):
    drop = ui.get('drop')
    if drop:
      os.remove(DBFILE)
      open(DBFILE, 'w+')

    tables = [Coin]
    db.connect()
    db.create_tables(tables, safe=True)

  @classmethod
  def disconnect(self):
    db.close()