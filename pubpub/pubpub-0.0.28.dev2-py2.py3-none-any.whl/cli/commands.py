import click
import functools
import os, io
from ..utils import get_working_directory, setup_logging, preserve_cwd, parse_markdown, to_absolute_path, to_absolute_paths
from ..resources import create_template
import logging
from ..processor import Processor


@click.group()
def main(**kwargs):
  """Wrapper for commands"""
  pass


# Convert to absolute path
def to_absolute_path_cb(ctx, param, value):
  """Convert value to absolute path"""
  return to_absolute_path(value)


def to_absolute_paths_cb(ctx, param, values):
  """A list of paths to absolute paths"""
  return [to_absolute_path(x) for x in values]


cmd_options = [
    click.option(
        '-d',
        '--directory',
        'directory',
        type=click.Path(),
        help="Directory of files"),
    click.option(
        '-i',
        '--input',
        'input_file',
        envvar='FILES',
        multiple=True,
        type=click.Path(),
        help="Jupyter notebooks to process."),
    click.option(
        '-c',
        '--cover_image',
        'cover_image',
        help='Cover image for output file',
    ),
    click.option(
        '-p', '--cover_pdf', 'cover_pdf', help='Cover pdf for output file'),
    click.option(
        '-o',
        '--ouput',
        'output',
        default='/tmp/complete.pdf',
        help="Output filename for output file"),
    click.option(
        '-v',
        '--virtualenv',
        'virtualenv',
        help="Virtual environment to execute the notebook"),
    click.option(
        '-w',
        '--working_directory',
        'working_directory',
        type=click.Path(),
        help="Working directory"),
    click.option('-t', '--template', 'template', help="Latex template"),
    click.option('-d', '--debug', count=True, help="Debug mode"),
    click.option(
        '-f',
        '--file',
        'file',
        envvar='BOOK_FILE',
        type=click.Path(exists=True)),
    click.option(
        '-a', '--assets', 'asset_files', help='Assets to copy', multiple=True),
    click.pass_context
]


def add_options(options):
  def _add_options(func):
    for option in reversed(options):
      func = option(func)
    return func

  return _add_options


# @main.command()
# @add_options(cmd_options)
# def pdf(ctx, **kwargs):
#   """Create a pdf from the source jupyter notebook

#   This runs through and executes the jupyter notebook
#   """
#   printer = Printer(**kwargs)
#   printer.pdf()

# @main.command()
# @add_options(cmd_options)
# def process_notebooks(ctx, **kwargs):
#   """Process notebooks

#   This runs through and creates latex files for each notebook
#   and writes out a chapter list for processing by other outputers
#   """
#   printer = Printer(**kwargs)
#   printer.build_notebooks()


@main.command()
@add_options(cmd_options)
@click.pass_context
def run_all(ctx, *args, **kwargs):
  """Run through"""
  setup_logging(kwargs.get('debug', 0))
  processor = Processor(**parse_opts(**kwargs))
  processor.run_all()


@main.command()
@add_options(cmd_options)
@click.pass_context
def html(ctx, *args, **kwargs):
  """Convert notebooks to html

  `html` runs through and creates html files for each notebook
  """
  setup_logging(kwargs.get('debug', 0))
  opts = parse_opts(**kwargs)

  processor = Processor(**opts)
  processor.to_html()


@main.command()
@add_options(cmd_options)
@click.pass_context
def toc(ctx, *args, **kwargs):
  """Generate table of contents for all files
  """
  setup_logging(kwargs.get('debug', 0))
  opts = parse_opts(**kwargs)

  processor = Processor(**opts)
  processor.add_toc()


@main.command()
@add_options(cmd_options)
def latex(ctx, *args, **kwargs):
  """Generate a latex document from notebook
  """
  setup_logging(kwargs.get('debug', 0))
  processor = Processor(**parse_opts(**kwargs))
  processor.to_latex()


@main.command()
@add_options(cmd_options)
def update_styles(ctx, *args, **kwargs):
  """Update the custom css
  """
  setup_logging(kwargs.get('debug', 0))
  Processor(**parse_opts(**kwargs)).update_styles()


@main.command()
@add_options(cmd_options)
def template(ctx, *args, **kwargs):
  """Create a latex template
  """
  setup_logging(kwargs.get('debug', 0))
  opts = parse_opts(**kwargs)

  tpl = create_template(None, **opts)
  output = opts.get('output')
  if output is None:
    output = '/tmp/template.tplx'
  with io.open(output, 'w') as f:
    f.write(tpl)


@main.command()
@add_options(cmd_options)
def pdf(ctx, *args, **kwargs):
  """Create a latex template
  """
  setup_logging(kwargs.get('debug', 0))
  input_file = kwargs.get('input_file')
  output = kwargs.get('output')

  Processor(**parse_opts(**kwargs)).to_pdf()


@main.command()
@add_options(cmd_options)
def create_snapshots(ctx, **kwargs):
  """Take snapshots from html"""
  setup_logging(kwargs.get('debug', 0))
  Processor(**parse_opts(**kwargs)).create_snapshots()


@main.command()
@add_options(cmd_options)
def cleanup(ctx, **kwargs):
  opts = parse_opts(**kwargs)
  processor = Processor(**opts)
  processor.cleanup()


def parse_opts(**kwargs):
  if 'file' in kwargs and kwargs.get('file') is not None:
    book_file = kwargs.get('file')
    book_filepath = get_working_directory(book_file)
    book_opts = parse_markdown(book_filepath)
    opts = kwargs.copy()
    opts.update(book_opts)
  elif 'input_file' in kwargs and kwargs.get('input_file') is not None:
    opts = kwargs.copy()
    files = []
    input_files = kwargs.get('input_file')
    for f in input_files:
      files.append(f)
    opts['files'] = files
    opts['base_dir'] = os.getcwd()

  return opts
