import clarus.services

def cashflows(output=None, **params):
    return clarus.services.api_request('Trade', 'Cashflows', output=output, **params)

def convert(output=None, **params):
    return clarus.services.api_request('Trade', 'Convert', output=output, **params)

def price(output=None, **params):
    return clarus.services.api_request('Trade', 'Price', output=output, **params)

def validate(output=None, **params):
    return clarus.services.api_request('Trade', 'Validate', output=output, **params)

