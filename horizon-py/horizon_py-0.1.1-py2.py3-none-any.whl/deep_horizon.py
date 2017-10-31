from api import Api


class DeepHorizon:

  def __init__(self, app_token=None, app_secret=None):
    self.api = Api(app_token, app_secret)

  def predict(self, features={}):
    return self.api.get('/predict', features)