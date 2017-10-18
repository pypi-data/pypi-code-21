from appdirs import *
from time import strftime
from ww import f as fstr
import os

APP_NAME = 'cryptofinder'
APP_UPPER = APP_NAME.upper()
APP_ENV = os.environ[fstr("{APP_UPPER}_ENV")]
APP_DIRS = AppDirs(APP_NAME, APP_NAME)
DBFILE = os.path.join( APP_DIRS.user_data_dir, fstr("{APP_NAME}.db") )
LOGFILE = os.path.join( APP_DIRS.user_log_dir, fstr("{APP_NAME}.log") )

class Config():
  def __init__(self):
    pass

  @classmethod
  def validate(self):
    files = [
      DBFILE,
      LOGFILE,
    ]

    directories = [
      APP_DIRS.user_data_dir,
      APP_DIRS.user_log_dir,
      APP_DIRS.user_cache_dir
    ]

    for directory in directories:
      if not os.path.isdir(directory):
        try:
          os.makedirs(directory)
        except OSError as e:
          print(e)
          return

    for file in files:
      if not os.path.isfile(file):
        try:
          open(file, 'w+').close()
        except OSError as e:
          print(e)
          return

    return True

  @classmethod
  def logfile(self):
    import logging
    logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)
    return logging.getLogger(__name__)