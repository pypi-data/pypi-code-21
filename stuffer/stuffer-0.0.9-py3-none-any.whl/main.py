"""Stuffer command line interface entrypoint."""

import getpass
import logging
from pathlib import Path

import os
import sys
from typing import List

import click

from stuffer import content
from stuffer import debconf
from stuffer import docker

from stuffer import apt
from stuffer import configuration
from stuffer import contrib
from stuffer import files
from stuffer import pip
from stuffer import store
from stuffer import system
from stuffer import user
from stuffer import utils
from stuffer.content import StringArg
from stuffer.core import Action, ActionRegistry


VERSION = "0.0.9"

os.environ['LANG'] = 'C.UTF-8'
os.environ['LC_ALL'] = 'C.UTF-8'


def _command_script(file_path: StringArg, operations: List[str]) -> str:
    if operations:
        if file_path:
            raise click.UsageError("Cannot pass both --file/-f and operations on command line")
        return "\n".join(operations) + "\n"
    logging.info("Reading commands from %s", file_path)
    with open(file_path) as f:
        contents = f.read()
        logging.info("Read %d bytes from %s", len(contents), file_path)
        return contents


def _script_substance(contents: str) -> str:
    all_lines = contents.splitlines()
    no_comments = [line for line in all_lines if not line.startswith('#')]
    return "\n".join([line for line in no_comments if line.strip()] + [''])


def _default_log_file() -> str:
    if getpass.getuser() == 'root':
        return "/var/log/stuffer.log"
    # noinspection PyTypeChecker
    return '{}/.stuffer/stuffer.log'.format(os.environ['HOME'])


def _default_store() -> str:
    if getpass.getuser() == 'root':
        return "/var/lib/stuffer/store"
    # noinspection PyTypeChecker
    return '{}/.stuffer/store'.format(os.environ['HOME'])


@click.command()
@click.option("--file", "-f", 'file_path',
              help='File to read commands from. Cannot be combined with commands on the command line.')
@click.option("--log-file", "-l", 'log_file', default=_default_log_file(),
              help='Path of log file. Defaults to /var/log/stuffer.log for root, and ~/.stuffer/stuffer.log otherwise')
@click.option('--quiet', '-q', is_flag=True,
              help="Do not log to stdout.")
@click.option("--store-dir", "-s", 'store_dir', default=_default_store(),
              help='Path to state store directory. Defaults to /var/lib/stuffer/store for root, and ~/.stuffer/store otherwise')
@click.option('--verbose', '-v', is_flag=True,
              help="Increase verbosity.")
@click.option('--version', '-V', is_flag=True,
              help='Print version number and exit.')
@click.argument("operations", nargs=-1)
def cli(file_path: str, log_file: str, quiet: bool, store_dir: str, verbose: bool, version: bool,
        operations: List[str]) -> None:
    """Command line interface entry point. See the `click documentation <http://click.pocoo.org/>`_ for details on the
    interface."""
    log = Path(log_file)
    log.parent.mkdir(parents=True, exist_ok=True)
    _setup_logging(log, verbose, quiet)
    if sys.version_info < (3, 5):
        logging.warning("This package is only known to work with python versions >= 3.5. Problems may arise.")
    if version:
        click.echo(VERSION)
        return

    configuration.config.store_directory = Path(store_dir)

    script = _command_script(file_path, operations)
    logging.debug("Read script:\n%s", script)
    full_command = _script_substance(script)
    logging.debug("Script substance:\n%s", full_command)
    action_namespace = {'apt': apt,
                        'configuration': configuration,
                        'content': content,
                        'contrib': contrib,
                        'debconf': debconf,
                        'docker': docker,
                        'files': files,
                        'pip': pip,
                        'store': store,
                        'system': system,
                        'user': user,
                        'utils': utils,
                        '__name__': __name__}
    if file_path:
        action_namespace['__file__'] = file_path
    if not Action.tmp_dir().is_dir():
        Action.tmp_dir().mkdir(parents=True)
    exec(full_command, action_namespace)

    actions = list(ActionRegistry.registered())
    logging.info("Loaded %d actions: %s", len(actions), ', '.join(map(repr, actions)))
    for act in actions:
        act.execute()


def _setup_logging(log_file: Path, verbose: bool, quiet: bool) -> None:
    logging.basicConfig(filename=str(log_file), filemode='a', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s : %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S')
    if not quiet:
        console = logging.StreamHandler(stream=sys.stdout)
        console.setLevel(logging.DEBUG if verbose else logging.INFO)
        # noinspection PyArgumentList
        formatter = logging.Formatter('%(levelname)-8s : %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


if __name__ == '__main__':
    sys.exit(cli())
