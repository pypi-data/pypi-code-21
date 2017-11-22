import hmac
import hashlib
import requests
import config

API_KEY = config.API_KEY
API_SECRET = config.API_SECRET

api_sign = hmac.new(API_SECRET, '/api/v1/strategies?id=1', hashlib.sha256).hexdigest()


from account import Account
from alarm import Alarm
from strategy import Strategy

compte = Account()
alarm  = Alarm()
strategy = Strategy()
strategy.getStrategies()

#alarm.create('BTC-USD',1,1,'<')
#compte.balance('BTC-USD',1)


