import clarus.services

def backtest(output=None, **params):
    return clarus.services.api_request('SIMM', 'BackTest', output=output, **params)

def impact(output=None, **params):
    return clarus.services.api_request('SIMM', 'Impact', output=output, **params)

def margin(output=None, **params):
    return clarus.services.api_request('SIMM', 'Margin', output=output, **params)

def sensitivity(output=None, **params):
    return clarus.services.api_request('SIMM', 'Sensitivity', output=output, **params)

