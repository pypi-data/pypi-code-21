# from pandocfilters import toJSONFilter, Str
import re

REGEXES = ((re.compile(r"\\begin{quote}(.*)\\end{quote}", re.DOTALL), r'''
  \\begin{framed}
  \\begin{quote}\1
  \\end{quote}
  \\end{framed}
  '''), )


def pretty_quotes(text, **kwargs):
  for p, replacement in REGEXES:
    text = p.sub(replacement, text)
  return text


def output_snapshots(text, **kwargs):
  return text
