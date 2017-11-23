from crypto_mediator.clients.client import MetaClient


kwargs = {'liqui': {}, 'poloniex': {}, 'bittrex': {'api_key': None, 'api_secret': None}}
client = MetaClient(**kwargs)


if __name__ == '__main__':
    liqui_ticker = client.ticker('liqui')
    poloniex_ticker = client.ticker('poloniex')
    bittrex_ticker = client.ticker('bittrex')

    liqui_pairs = client.pairs('liqui')
    poloniex_pairs = client.pairs('poloniex')
    bittrex_pairs = client.pairs('bittrex')

    import pdb
    pdb.set_trace()