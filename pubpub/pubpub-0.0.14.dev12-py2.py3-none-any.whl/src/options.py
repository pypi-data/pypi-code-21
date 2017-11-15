import frontmatter
import os


def parse_markdown(file):
  """Parses the book.md"""
  build_dir = os.path.abspath(os.path.dirname(file))
  opts = _parse_markdown(file)

  files = []
  for file in opts.content.split('\n'):
    files.append(file)

  opts['files'] = files

  opts['base_dir'] = build_dir
  return opts


def _parse_markdown(file):
  with open(file) as f:
    return frontmatter.load(f)
