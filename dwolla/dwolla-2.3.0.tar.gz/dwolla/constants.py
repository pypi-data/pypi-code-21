client_id = 'YOUR ID HERE'
client_secret = 'YOUR SECRET HERE'
pin = 1234

oauth_scope = 'Send|Transactions|Balance|Request|Contacts|AccountInfoFull|Funding|ManageAccount|Scheduled'
access_token = 'OAUTH TOKENS GO HERE'

# Hostnames, endpoints
production_host = 'https://www.dwolla.com/'
sandbox_host = 'https://sandbox.dwolla.com/'
default_postfix = 'oauth/rest'

# Client behavior
sandbox = True
debug = True
rest_timeout = 15
proxy = False

'''
Note about the `proxy` parameter:

Proxies are stored in a dictionary organized as {'protocol': 'proxy:port'},
you must specify proxies for both http and https for proper coverage.

An example of this is below:

proxy = {
    'http': 'http://someproxy:someport',
    'https': 'https://anotherproxy:anotherport'
}
'''
