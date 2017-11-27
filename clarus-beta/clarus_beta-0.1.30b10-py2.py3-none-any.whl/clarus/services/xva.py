import clarus.services

def fva(output=None, **params):
    return clarus.services.api_request('XVA', 'FVA', output=output, **params)

def mva(output=None, **params):
    return clarus.services.api_request('XVA', 'MVA', output=output, **params)

