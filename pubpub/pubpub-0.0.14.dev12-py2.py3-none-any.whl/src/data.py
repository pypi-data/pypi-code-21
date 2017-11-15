from __future__ import print_function
import os
from scss import Compiler
from collections import defaultdict
from jinja2 import Template


def data_dir():
  """Data directory"""
  this_dir = os.path.dirname(__file__)
  data_dir = os.path.join(this_dir, '..', 'data')
  return data_dir


def compiled_scss():
  p = Compiler()
  scss_file = os.path.join(data_dir(), 'style.scss')
  with open(scss_file, 'r') as f:
    compiled = p.compile_string(f.read())
    return compiled


def empty_notebook_path():
  return os.path.join(data_dir(), "empty_notebook.ipynb")


def read_html(**attrs):
  """Read html"""
  defaults = {
      'title': 'title',
      'description': 'description',
      'body': '',
      'authors': [],
      'styles': compiled_scss()
  }
  defaults.update(**attrs)
  with open(os.path.join(data_dir(), 'main.html'), 'r') as f:
    template = Template(f.read())
    return template.render(**defaults)
