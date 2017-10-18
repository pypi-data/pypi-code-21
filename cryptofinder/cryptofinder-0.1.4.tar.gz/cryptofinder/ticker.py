from .config import APP_DIRS
from .models import Coin
import datetime

class Ticker:
  def __init__(self):
    self.path = os.path.join(APP_DIRS.user_data_dir, 'ticker.p')

  @property
  def cached(self):
    if not os.path.isfile(self.path):
      return
    return pickle.load( open( self.path, "rb" ) )

  @property
  def date(self):
    if not os.path.isfile(self.path):
      return
    return list(self.cached)[-1].get('date')

  @property
  def stale(self):
    if not self.date:
      return
    if datetime.datetime.now() > ( self.date + datetime.timedelta(minutes = 10) ):
      return True

  @property
  def entries(self):
    try:
      return requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
    except ConnectionError as e:
      logger.error(e)
      return

  def refresh(self):
    entries = list(self.entries)
    entries.append( { 'date': datetime.datetime.now() } )
    pickle.dump( entries, open( self.path, "wb" ) )
    return True

  def parse(self):
    entries = list(self.cached)
    for entry in tqdm(entries, desc="Updating coins", unit=" coins"):
      entry = dict(entry)
      slug = str(entry.get('id'))

      coin, added = Coin.get_or_create(slug=slug)

      coin.name = str( entry.get('name') )
      coin.symbol = str( entry.get('symbol') )
      coin.rank = int( entry.get('rank') or 0 )
      coin.percent_change_1h = float( entry.get('percent_change_1h') or 0 )
      coin.percent_change_24h = float( entry.get('percent_change_24h') or 0 )
      coin.percent_change_7d = float( entry.get('percent_change_7d') or 0 )
      coin.price_btc = float( entry.get('price_btc') or 0 )
      coin.price_usd = float( entry.get('price_usd') or 0 )
      last_updated = int( entry.get('last_updated') or 0 )
      if last_updated:
        coin.last_updated = datetime.datetime.utcfromtimestamp(last_updated)

      day_volume = float( entry.get('24h_volume_usd') or 0 )
      market_cap = float( entry.get('market_cap_usd') or 0 )
      coin.day_volume = day_volume
      coin.market_cap = market_cap
      if (day_volume and market_cap):
        coin.day_volume_ratio = day_volume / market_cap

      avail_supply = float( entry.get('available_supply') or 0 )
      total_supply = total_supply = float( entry.get('total_supply') or 0 )
      coin.avail_supply = avail_supply
      coin.total_supply = total_supply
      if (avail_supply and total_supply):
        coin.avail_supply_ratio = avail_supply / total_supply

      coin.save()

    return True