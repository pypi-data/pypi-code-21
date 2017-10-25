#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Console script for coordinator_data_tasks."""
# Imports
import typing as t
import logging
from pathlib import Path


from munch import Munch

import click

import logzero
from logzero import logger as log

from coordinator_data_tasks import commands
from coordinator_data_tasks.utils import errors as e


VERB_LVLS = {"quiet": logging.ERROR, "normal": logging.INFO, "noisy": logging.DEBUG}


@click.group(invoke_without_command=True)
@click.option("-v", "--verbosity", default="normal", type=click.Choice(list(VERB_LVLS.keys())),
              help=f"Set the level of logging messages printed to the screen. Options: {list(VERB_LVLS.keys())}",
              show_default=True)
@click.pass_context
def main(ctx, verbosity):
    """Command line interface to the coordinator_data_tasks library.

    For command specific help text, call the specific
    command followed by the --help option.
    """
    ctx.obj = Munch()
    ctx.obj.CONFIG = Munch()

    # Set log level
    logzero.loglevel(VERB_LVLS[verbosity])


@main.group()
@click.pass_context
def join(ctx):
    """Sub-command for performing "join" type operations on data tables.

    For command specific help text, call the specific
    command followed by the --help option.
    """


@join.command(name="left")
@click.option('-l', '--left',
              type=click.Path(exists=True),
              help="[Required] Path to the xls file we will use as the left table.",
              default=None)
@click.option('-r', '--right',
              type=click.Path(exists=True),
              help="[Required] Path to the xls file we will use as the right table.",
              default=None)
@click.option('-j', '--join-on',
              type=click.STRING,
              help="[Required] The text following this option will be used as a column that we will use as a join column. "
              "This option can be repeated for each column you want to join on. "
              "NOTE: If the column contains spaces, you must surround the text with quotes. Exp: 'This is the column name'",
              multiple=True)
@click.option('-o', '--out',
              type=click.Path(),
              help="Path to use for the resulting table.",
              show_default=True,
              default="left_join_result.xls")
@click.pass_context
def left_join(ctx, left, right, join_on, out):
    """Left join excel sheets (left, right) on columns (join-on)."""
    if (left is None) or (right is None):
        msg = "You MUST provide a value for both 'left' and 'right'."
        log.error(msg)
        raise e.ValidationError(msg)

    if not join_on:
        msg = "You MUST provide at least one value of 'join-on'."
        log.error(msg)
        raise e.ValidationError(msg)

    commands.left_join.main(left_path=Path(left), right_path=Path(right), join_on=join_on, out=Path(out), indicator=True)


