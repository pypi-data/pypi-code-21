#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
import shlex
import subprocess

import click
from pkg_resources import get_distribution
from semantic_version import Version

__author__ = "john"


@click.group()
def cli():
  """CLI utilities"""


@cli.command('rel')
@click.option('-n', '--num')
def release(num):
  """Release prod

  Notes:
    setup.py develop
    setup.py develop --uninstall
  """
  cmd('pip uninstall webstarts')
  cmd('python setup.py develop')
  version = num or _bump()
  cmd(f'git hf release start {version}')
  cmd(f'git hf release finish -M {version}')
  cmd('git checkout master')
  cmd('./deploy.sh')
  cmd('git checkout develop')


@cli.command()
def version():
  return print(f'Version: {_version()}')


@cli.command()
def bump():
  return print(f'Next Version: {_bump()}')


def _version():
  return get_distribution('webstarts').version


def _bump():
  v = Version.coerce(_version())
  if v.minor >= 9:
    return v.next_major()
  return v.next_minor()


def cmd(line, **kwargs):
  print(line)
  return subprocess.run(shlex.split(line), check=True, stdout=subprocess.PIPE, encoding='utf-8', **kwargs)
