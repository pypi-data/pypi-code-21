import sys
import os
import glob

import jinja2
from jinja2_markdown import MarkdownExtension

from . import __version__


jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
jinja_env.add_extension(MarkdownExtension)


def make_page(source_file_path: str) -> None:
    source_file_directory = os.path.dirname(source_file_path)
    output_file_path = os.path.join(source_file_directory, 'index.html')
    with open(output_file_path, 'w') as f:
        f.write(jinja_env.get_template(source_file_path).render())

    print(output_file_path)
    return output_file_path


def build_adventure() -> None:
    glob_pattern = os.path.join('.', '*', '_TRAPMK')
    if not list(map(make_page, glob.iglob(glob_pattern, recursive=True))):
        print("No source files matched pattern: %s" % source_path_pattern)
        sys.exit(1)


def entrypoint():
    if '--version' in sys.argv:
        print("trapmk v" + __version__)
    else:
        build_adventure()
