# from pandocfilters import toJSONFilter, Str
import re

CODE_REGEXES = (
    (re.compile(r"\\begin{quote}(.*)\\end{quote}", re.DOTALL), r'''
\\begin{framed}
\\begin{quote}\1
\\end{quote}
\\end{framed}
  '''),
    (re.compile(r"\\includegraphics(.*)$"), r'''
\\begin{center}
\\includegraphics\1\n\\end{center}
  '''),
)

MARKDOWN_REGEXES = ((re.compile("\^"), '\\textasciicircum'), )


def pretty_quotes(text, **kwargs):
  for p, replacement in CODE_REGEXES:
    text = p.sub(replacement, text)
  return text


def pretty_markdown(text, **kwargs):
  for p, replacement in MARKDOWN_REGEXES:
    text = p.sub(replacement, text)
  return text


def output_snapshots(text, **kwargs):
  return text
