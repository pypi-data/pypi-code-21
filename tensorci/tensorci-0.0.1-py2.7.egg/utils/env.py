import os

environment = os.environ.get('ENVIRON')

if environment:
  assert environment in ('test', 'dev', 'stating', 'prod')
  ENV = environment.lower()
else:
  ENV = 'prod'


def env():
  return ENV


def is_test():
  return ENV == 'test'


def is_dev():
  return ENV == 'dev'


def is_staging():
  return ENV == 'staging'


def is_prod():
  return ENV == 'prod'