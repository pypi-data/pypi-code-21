from humanfriendly import format_number as fint
from tabulate import tabulate
from ww import f as fstr
import datetime
import json
import os

class CoinView:
  def __init__(self, coins):
    self.coins = coins

  def table(self):
    table_data = []
    count = 1
    for coin in self.coins:
      dv = fint(coin.day_volume)
      mc = fint(coin.market_cap)

      row = []
      row.append(count)
      row.append(coin.symbol)
      row.append(coin.name)
      row.append(fint(coin.total_supply))
      row.append(fint(coin.avail_supply))
      row.append(coin.avail_supply_ratio)
      row.append(fstr("${dv}"))
      row.append(fstr("${mc}"))
      row.append(coin.day_volume_ratio)
      row.append(coin.price_btc)
      row.append(fstr("${coin.price_usd}"))
      row.append(coin.percent_change_1h)
      row.append(coin.percent_change_24h)
      row.append(coin.percent_change_7d)

      row.append(coin.rank)
      table_data.append(row)
      count += 1

    table_headers = [
      '#', # count
      'Symbol', # symbol
      'Name', # name
      'Total Supply', # total_supply
      'Avail. Supply', # avail_supply
      'Ratio', # avail_supply_ratio
      'Daily Volume', # day_volume
      'Market Cap', # market_cap
      'Ratio', # day_volume_ratio
      'BTC', # price_btc
      'USD', # price_usd
      '%1H', # percent_change_1h
      '%24H', # percent_change_24h
      '%7D', # percent_change_7d
      'Rank', # rank
    ]

    table_formats = [
      '.1f', # count
      '.1f', # symbol
      '.1f', # name
      '.1f', # total_supply
      '.1f', # avail_supply
      '.2f', # avail_supply_ratio
      '.2f', # day_volume
      '.0f', # market_cap
      '.3f', # day_volume_ratio
      '.8f', # price_btc
      '.6f', # price_usd
      '+.2f', # percent_change_1h
      '+.2f', # percent_change_24h
      '+.2f', # percent_change_7d
      '.1f', # rank
    ]

    table = tabulate(table_data, headers=table_headers, floatfmt=table_formats, numalign="left")

    logger.info('')
    logger.info('Results:', color="green")
    logger.info('')
    logger.info(table, color="green")
    logger.info('')

  def json(self):
    data = []
    for coin in self.coins:
      data.append(str(coin))

    if data:
      timestamp = datetime.datetime.now()
      filename = fstr("{timestamp}-cryptofinder-results.json")
      outfile = os.path.join(os.getcwd(), filename)
      with open(outfile, 'w') as outfile:
        json.dump(data, outfile)