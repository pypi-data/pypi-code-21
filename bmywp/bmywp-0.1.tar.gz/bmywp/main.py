import hmac
import config
import hashlib
import requests
import tortilla

API_KEY    = config.API_KEY
API_SECRET = config.API_SECRET
API_URL    = config.API_URL


api_sign = hmac.new(API_SECRET, '/api/v1/strategies', hashlib.sha256).hexdigest()

'''
response = requests.get(
  'https://test.bmybit.com/api/v1/strategies',
  headers={
    'X-Api-Key': API_KEY,
    'X-Api-Sign': api_sign
  },
)

print response.content
'''


bmybit = tortilla.wrap('https://test.bmybit.com/api/v1')

bmybit.config.headers['X-Api-Key'] = API_KEY
bmybit.config.headers['api_sign']  = api_sign

print bmybit.config.headers

res = bmybit.get('strategies',params = {'id':330},  headers={
    'X-Api-Key': API_KEY,
    'X-Api-Sign': api_sign
  })

print res

