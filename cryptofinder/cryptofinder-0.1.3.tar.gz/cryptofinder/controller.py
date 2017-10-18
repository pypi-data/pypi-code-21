from .models import Coin, Database
from .ticker import Ticker
from .util import datetime_formatted
from .views import CoinView

class Controller:
  @classmethod
  def main(self):
    Database.connect()

    # Set local variables for user input
    avail_supply_ratio = ui.get('avail_supply_ratio')
    day_volume_ratio = ui.get('day_volume_ratio')
    market_cap = ui.get('market_cap')
    avail_supply = ui.get('avail_supply')
    day_volume = ui.get('day_volume')
    
    drop = ui.get('drop')
    force = ui.get('force')
    save = ui.get('save')
    offline = ui.get('offline')
    quiet = ui.get('quiet')

    # Update ticker
    ticker = Ticker()
    current = False
    if ticker.cached:
      logger.debug("Ticker is cached.")

      if ticker.stale:
        logger.debug("Ticker is stale.")
      else:
        logger.debug("Ticker is not stale.")
        if len(ticker.cached) == len(Coin.select()):
          current = True
    else:
      logger.debug("Ticker is not cached.")
      if offline:
        logger.error("Nothing to parse.")
        return

    # Update coins
    if force or drop or not current:
      if not ticker.refresh():
        logger.error("Ticker refresh failed.")
        return
      if not ticker.parse():
        logger.error("Ticker parse failed.")
        return
      logger.debug("Ticker updated.")

    # Select coins
    coins = Coin.select().where(
      Coin.avail_supply <= avail_supply[1],
      Coin.avail_supply >= avail_supply[0], 
      Coin.avail_supply_ratio >= avail_supply_ratio,
      Coin.day_volume_ratio >= day_volume_ratio, 
      Coin.day_volume <= day_volume[1],
      Coin.day_volume >= day_volume[0],
      Coin.market_cap <= market_cap[1],
      Coin.market_cap >= market_cap[0], 
    )

    # Output results
    view = CoinView(coins)
    
    if not quiet:
      view.table()
      dt = datetime_formatted(ticker.date)
      ticker_date = dt.get('date')
      ticker_time = dt.get('time')
      logger.info( fstr("Data cached {ticker_date} @ {ticker_time}.") )

    if save:
      view.json()

    Database.disconnect()

    return True