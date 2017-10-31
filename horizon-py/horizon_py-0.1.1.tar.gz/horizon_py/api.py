import os
import requests
import json


class Api:

  def __init__(self, app_token=None, app_secret=None):
    self.app_token = app_token or os.environ.get('DEEP_HORIZON_TOKEN')
    self.app_secret = app_secret or os.environ.get('DEEP_HORIZON_SECRET')
    base_url = os.environ.get('DEEP_HORIZON_URL') or 'https://www.deephorizon.io'

    if base_url.endswith('/'):
      base_url = base_url[:-1]

    self.url = base_url + '/api'

  def get(self, path, args={}):
    return self.request('get', path, args)

  def post(self, path, args={}):
    return self.request('post', path, args)

  def put(self, path, args={}):
    return self.request('put', path, args)

  def delete(self, path, args={}):
    return self.request('delete', path, args)

  def request(self, method, path, args={}):
    if not self.app_token or not self.app_secret:
      raise StandardError('DeepHorizon API not configured. Make sure app_token and app_secret '
                          'are provided during client instantiation or as environment variables '
                          'DEEP_HORIZON_TOKEN and DEEP_HORIZON_SECRET, respectively.')

    func = getattr(requests, method)

    resp = func(self.url + path, args,
                headers={'Deep-Horizon-Token': self.app_secret})

    try:
      resp_body = json.loads(resp.content)
    except:
      resp_body = {'ok': False, 'error': 'unknown_error'}

    return resp_body