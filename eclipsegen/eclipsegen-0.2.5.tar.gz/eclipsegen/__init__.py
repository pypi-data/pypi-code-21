import os

_PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
_DIRECTOR_PATH = os.path.join(_PACKAGE_PATH, 'director')

def director_path():
  return _DIRECTOR_PATH
