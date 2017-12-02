import os
from utils.env import env


class Config:
  DEBUG = True


class ProdConfig(Config):
  DEBUG = False

  def __init__(self):
    self.DOMAIN = os.environ.get('TENSORCI_DOMAIN') or 'app.tensorci.com'
    self.API_URL = 'http://{}/api'.format(self.DOMAIN)


class StagingConfig(Config):
  DEBUG = False

  def __init__(self):
    self.DOMAIN = os.environ.get('TENSORCI_DOMAIN') or 'staging.app.tensorci.com'
    self.API_URL = 'http://{}/api'.format(self.DOMAIN)


class DevConfig(Config):

  def __init__(self):
    self.DOMAIN = os.environ.get('TENSORCI_DOMAIN') or 'dev.app.tensorci.com'
    self.API_URL = 'http://{}/api'.format(self.DOMAIN)


class TestConfig(Config):

  def __init__(self):
    self.DOMAIN = os.environ.get('TENSORCI_DOMAIN') or 'localhost'
    self.API_URL = 'http://{}/api'.format(self.DOMAIN)


def get_config():
  config_class = globals().get('{}Config'.format(env().capitalize()))
  return config_class()


config = get_config()