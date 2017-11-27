import clarus.services

def predict(output=None, **params):
    return clarus.services.api_request('ProfitLoss', 'Predict', output=output, **params)

