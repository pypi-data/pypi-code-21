import os


def env():
  provided_env = os.environ.get('DEEP_HORIZON_ENV')

  if provided_env and provided_env.lower() in ['test', 'dev']:
    return provided_env.lower()

  return 'prod'