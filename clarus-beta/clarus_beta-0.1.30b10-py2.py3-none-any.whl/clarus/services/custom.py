import clarus.services

def collateralbalances(output=None, **params):
    return clarus.services.api_request('Custom', 'CollateralBalances', output=output, **params)

