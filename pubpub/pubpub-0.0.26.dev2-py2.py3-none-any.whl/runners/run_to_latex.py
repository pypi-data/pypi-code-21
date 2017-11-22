import os, io, base64
import nbformat
import json
import re
from ..utils import get_working_directory, preserve_cwd, execute_in_virtualenv

from traitlets.config import Config
from nbconvert.exporters.latex import LatexExporter

MARKDOWN_REGEXES = (
    # (re.compile("\^"), '\\\\textasciicircum'),
    (re.compile("\ˆ"), '\\\\textasciicircum'), )


def pretty_markdown(text, **kwargs):
  for p, replacement in MARKDOWN_REGEXES:
    text = p.sub(replacement, text)
  return text


@preserve_cwd
def run_to_latex(processed_file, output_filename, snapshots, **opts):

  title = opts.get('title')
  working_directory = opts.get('working_directory')
  template = opts.get('template')
  virtualenv_name = opts.get('virtualenv_name')

  c = Config()
  c.execute = False
  exporter = LatexExporter(config=c)
  with io.open(processed_file, 'r') as f:
    nb = nbformat.reads(f.read(), as_version=4)

  # {'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': "data = np.vstack([data1, data2, data3, data4]).transpose()\ndf = pd.DataFrame(data, columns=['data1', 'data2', 'data3', 'data4'])\ndf.head()"}
  i = 0
  cells = [
    #       nbformat.v4.new_code_cell("""
    # from IPython.display import Image
    # from IPython.core.display import HTML
    #   """)
  ]
  for x, cell in enumerate(nb.cells):
    new_cell = cell
    if cell['cell_type'] == 'code':
      if 'outputs' in cell and len(cell['outputs']) > 0:
        # TODO: Fix this for only non-image outputs
        with open(snapshots[i], 'rb') as f:
          new_cell.outputs = [
              nbformat.v4.new_output('display_data', {
                  'image/png': base64.b64encode(f.read())
              })
          ]
          # new_cell = nbformat.v4.new_code_cell(
          #     cell_type=new_cell['cell_type'],
          #     execution_count=new_cell['execution_count'],
          #     metadata=new_cell['metadata'],
          #     source=new_cell['source'],
          #     outputs=[
          #         nbformat.v4.new_output(
          #             'display_data', {
          #                 'image/png': base64.b64encode(f.read())
          #             })
          #     ])
        i = i + 1
    else:
      new_cell['source'] = pretty_markdown(new_cell['source'])
    cells.append(new_cell)
    # parsed = json.loads(output)
    # print(json.dumps(parsed, indent=True))
    #     i = i + 1
    #     print(output)
    #     nb.cells[i] = nbformat.v4.new_markdown_cell("CODE CELL")
  new_book = nbformat.v4.new_notebook()
  new_book['cells'] = cells
  new_book['metadata'].name = title

  with open(processed_file, 'w') as f:
    nbformat.write(new_book, f)

  # print(nb.cells[i])

  config_file = os.path.join(os.path.dirname(__file__), '..', 'config.py')
  args = [
      'jupyter',
      'nbconvert',
      '--to',
      'latex',
      '--config %s' % config_file,
      '--output',
      output_filename,
  ]

  if template is not None:
    args.append(
        '--template %s' % get_working_directory(template, working_directory))

  args.append("\"%s\"" % processed_file)

  os.chdir(working_directory)
  output = execute_in_virtualenv(args, virtualenv_name)

  return output
