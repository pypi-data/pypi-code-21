import os
import sys
import stat
import subprocess
import shutil
import click
import requests
import time
from configparser import ConfigParser
import getpass

APP_DIR = click.get_app_dir('juantap')
CONFIG_PATH = os.path.join(APP_DIR, 'config.ini')

click.echo(CONFIG_PATH)

CFG = ConfigParser()

def write_config():
    with open(CONFIG_PATH, 'w') as cfg_file:
        CFG.write(cfg_file)

def default_config():
    CFG['system'] = {
        'JuantapUser' : getpass.getuser(),
        'RootServerDir' : os.path.expanduser('~/rootserver'),
        'InstancesDir' : os.path.expanduser('~/instances'),
        'NumberOfInstances' : 2,
        'BaseHostname': "Juantap",
    }
    write_config()

if not os.path.exists(CONFIG_PATH):
    os.makedirs(APP_DIR, exist_ok=True)
    default_config()

CFG.read(CONFIG_PATH)

if 'system' not in CFG.sections():
    click.echo("Malformed config file!")
    if click.confirm("Do you want to reset the config?"):
        default_config()
    else:
        sys.exit(1)

@click.group()
def cli():
    """
    CLI for managing multiple csgo server instances and their root server.

    Harnesses the power of overlayfs
    """
    pass

from . import config, instances, root

cli.add_command(config.config)
cli.add_command(instances.instances)
cli.add_command(root.root)
