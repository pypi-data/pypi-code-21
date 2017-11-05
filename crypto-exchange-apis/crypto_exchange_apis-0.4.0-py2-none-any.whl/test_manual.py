from crypto_exchange_apis import itBit
from crypto_exchange_apis import Bitfinex
from crypto_exchange_apis import Bitstamp
from crypto_exchange_apis import GDAX
from crypto_exchange_apis import Bittrex
from crypto_exchange_apis import Poloniex
from crypto_exchange_apis import Tuxexchange


itbit = itBit()

print('itBit tests:')
print(str(itbit.get_ticker())[0:77]+'...') # Conversion to string and [0:77] are just to keep output on one terminal line -- use itbit.get_ticker() in practice
print(str(itbit.get_order_book())[0:77]+'...')

bitfinex = Bitfinex()

print('Bitfinex tests:')
print(str(bitfinex.ticker())[0:77]+'...')
print(str(bitfinex.ticker2())[0:77]+'...')

bitstamp = Bitstamp()

print('Bitstamp tests:')
print(str(bitstamp.ticker())[0:77]+'...')
print(str(bitstamp.order_book())[0:77]+'...')

gdax = GDAX()

print('GDAX tests:')
print(str(gdax.get_product_ticker())[0:77]+'...') # Conversion to string and [0:77] are just to keep output on one terminal line -- use itbit.get_ticker() in practice
print(str(gdax.get_product_order_book())[0:77]+'...')

bittrex = Bittrex()

print('Bittrex tests:')
print(str(bittrex.get_currencies())[0:77]+'...')
print(str(bittrex.get_markets())[0:77]+'...')

poloniex = Poloniex()

print('Poloniex tests:')
print(str(poloniex.returnTicker()['BTC_XMR'])[0:77]+'...')
print(str(poloniex.returnCurrencies())[0:77]+'...')

tuxexchange = Tuxexchange()

print('Tux Exchange tests:')
print(str(tuxexchange.api_query('getcoins'))[0:77]+'...')
print(str(tuxexchange.api_query('getticker'))[0:77]+'...')
