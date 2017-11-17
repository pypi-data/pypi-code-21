from __future__ import print_function
import os
from scss import Compiler
from collections import defaultdict
import io
from jinja2 import Template


def data_dir():
  """Data directory"""
  this_dir = os.path.dirname(__file__)
  data_dir = os.path.join(this_dir)
  return data_dir


def create_template(**opts):
  tpl = os.path.join(data_dir(), 'raw_template.tex')
  # with io.open(os.path.join(data_dir(), 'jupyter_latex.sty'), 'r') as f:
  #   jupyter_latex = f.read()

  # with io.open(os.path.join(data_dir(), 'pygment_definitions.sty'), 'r') as f:
  #   pygment_definitions = f.read()

  defaults = {}
  defaults.update(opts)

  with io.open(tpl, 'r') as f:
    return Template(f.read()).render(**defaults)


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
