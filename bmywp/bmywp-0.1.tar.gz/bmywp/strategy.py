from main import bmybit

class Strategy():

    def getStrategy(self, id):
        try:
            bmybit.get('/strategies',
                        params={'id': id})
        except:
            print 'Could not get strategy'

    def getStrategies(self):
        try:
            bmybit.get('/strategies')
        except:
            print 'Could not get strategies'

    def startStrategy(self, exchange, pair, currency, amout, level, risk, lockin):
        try:
            bmybit.get('/strategies/start',
                        params={'exchange':   exchange,
                              'pair':       pair,
                              'currency':   currency,
                              'condition':  amount,
			      'level':      level,
			      'risk':       risk,
			      'lockin':     lockin})
        except:
            print 'Could not start the strategy'

    def terminateStrategy():
        try:
            bmybit.get('/strategies/terminate',
                        params={'id': id})
        except:
            print 'Could not terminate the strategy'
