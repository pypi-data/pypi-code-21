#!/usr/bin/env python3

import click
import logging
import sys

import portinus

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group()
@click.option('-v', '--verbose', count=True, help="Enable more logging. More -v's for more logging")
def task(verbose):
    log_level = logging.WARNING
    if verbose == 1:
        log_level = logging.INFO
    if verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)


@task.command()
@click.option('--name', required=True, help="The name of the service to remove")
def check(name):
    try:
        portinus.monitor.checker.run(name)
    except PermissionError:
        sys.exit(1)


if __name__ == "__main__":
    task()
