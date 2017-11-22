from main import bmybit

class Account():

    def balance(self, exchange, pair):
	try:
    	    bmybit.get('/accounts/balance',
 			params={'exchange': exchange,
				'pair':pair})
	except:
    	    print 'Could not get account balance'

    def info(self):
        try:
            bmybit.get('/accounts/info')
        except:
            print 'Could not get account info'



