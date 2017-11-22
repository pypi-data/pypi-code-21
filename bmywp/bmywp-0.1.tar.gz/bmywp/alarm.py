from main import bmybit

class Alarm():

    def create(self, exchange, pair, price, condition):
        try:
            bmybit.post('/alarms',
                        data={'exchange':   exchange,
                              'pair':       pair,
			      'price':      price,
			      'condition':  condition})
        except:
            print 'Could not create alarm'

    def get(self, exchange=None, pair=None):
        try:
            bmybit.get('/alarms',
                        params={'exchange': exchange,
                                'pair':pair})
        except:
            print 'Could not get alarms'


