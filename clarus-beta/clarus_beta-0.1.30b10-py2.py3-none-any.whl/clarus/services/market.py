import clarus.services

def curveusage(output=None, **params):
    return clarus.services.api_request('Market', 'CurveUsage', output=output, **params)

def df(output=None, **params):
    return clarus.services.api_request('Market', 'DF', output=output, **params)

def fixings(output=None, **params):
    return clarus.services.api_request('Market', 'Fixings', output=output, **params)

def fxrates(output=None, **params):
    return clarus.services.api_request('Market', 'FXRates', output=output, **params)

def pardv01(output=None, **params):
    return clarus.services.api_request('Market', 'ParDV01', output=output, **params)

def parrates(output=None, **params):
    return clarus.services.api_request('Market', 'ParRates', output=output, **params)

def zerorates(output=None, **params):
    return clarus.services.api_request('Market', 'ZeroRates', output=output, **params)

