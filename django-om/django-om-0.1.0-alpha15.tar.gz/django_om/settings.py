import importlib
import os

from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = settings.DEBUG

SETTINGS = settings.DJANGO_OM

ENCODING = SETTINGS.get('TRANSIT_ENCODING', 'json')
PAGE_SIZE = SETTINGS.get('PAGE_SIZE', 20)

PARSER = importlib.import_module(SETTINGS['PARSER']).PARSER
