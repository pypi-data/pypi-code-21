#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click

from jawa.cli.disassemble import dism
from jawa.cli.info import info


@click.group()
def cli():
    pass

cli.add_command(dism)
cli.add_command(info)
