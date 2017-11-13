import yaml
import sys
import importlib.util
from pyrses import AsciiApp

def start(app: AsciiApp) -> None:
    print('starting {}...'.format(app.name))
    print('quiting {}...'.format(app.name))

def cli():
    pass

