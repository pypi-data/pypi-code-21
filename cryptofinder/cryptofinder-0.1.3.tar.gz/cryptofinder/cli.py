from .config import Config, APP_ENV
from .controller import Controller
from .logger import Logger
from tqdm import tqdm
import builtins
import json
import requests
import click
import os
import pickle
from ww import f as fstr
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
if APP_ENV == 'development':
  from behold import Behold
  from pprint import pprint as pp

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--market-cap', default=(0.0, 250000.0), show_default=True, nargs=2, type=float, help='Market cap range.', metavar='<float[]>')
@click.option('--avail-supply', default=(0.0, 50000000.0), nargs=2, show_default=True, type=float, help='Available supply range.', metavar='<float[]>')
@click.option('--avail-supply-ratio', default=0.5, show_default=True, help='This * total supply >= circulating supply.', metavar='<float>')
@click.option('--day-volume', default=(0.0, float('inf')), show_default=True, nargs=2, type=float, help='Daily volume range.', metavar='<float[]>')
@click.option('--day-volume-ratio', default=0.02, show_default=True, help='This * market cap >= day volume.', metavar='<float>')

@click.option('--force', default=False, is_flag=True, help='Force coin instance updates.')
@click.option('--drop', default=False, is_flag=True, help='Drop database.')
@click.option('--offline', default=False, is_flag=True, help='Disable ticker updates.')
@click.option('--save', default=False, is_flag=True, help='Save results to JSON file.')
@click.option('-v', '--verbose', default=False, is_flag=True, help='Enable verbose logging.')
@click.option('-q', '--quiet', default=False, is_flag=True, help='Disable stdout logging.')

def cli(**kwargs):
  if Config.validate():
    builtins.ui = {k: v for k, v in kwargs.items() if v}
    builtins.os = os
    builtins.fstr = fstr
    builtins.json = json
    builtins.tqdm = tqdm
    builtins.requests = requests
    builtins.pickle = pickle
    builtins.logger = Logger(ui)

    if APP_ENV == 'development':
      pp('hi')
      logger.info("Development mode enabled.", color="green")
      builtins.Behold = Behold
      builtins.pp = pp
    
    if Controller.main():
      status = 0
    else:
      status = 1
    logger.info('')
    logger.info("Exiting.")
    return status

def main():
  cli(obj={})

if __name__ == '__main__':
  main()