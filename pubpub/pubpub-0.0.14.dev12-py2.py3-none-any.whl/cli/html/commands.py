import click
import functools
from pubpub.src import get_working_directory, setup_logging, preserve_cwd, parse_markdown
import logging
from pubpub.src import Processor


@click.group()
def main(**kwargs):
  pass


@main.command()
@click.option('-f', '--file', 'file', envvar='BOOK_FILE', default='./book.md')
@click.option(
    '-o',
    '--ouput',
    'output',
    default='/tmp/pubpub.pdf',
    help="Output filename for output file")
@click.option('-t', '--template', 'template', help="Latex template")
@click.option('-d', '--debug', count=True)
@click.pass_context
def html(ctx, *args, **kwargs):
  """Process from a book.md file"""

  setup_logging(kwargs.get('debug', 0))

  book_file = kwargs.get('file')
  book_filepath = get_working_directory(book_file)
  opts = parse_markdown(book_filepath)

  processor = Processor(**opts)
  processor.to_html()
