import io, os, nbformat
from jinja2 import DictLoader, Template, FileSystemLoader

import base64, binascii
import re
from ..utils import get_working_directory, preserve_cwd, execute_in_virtualenv

from traitlets.config import Config
from nbconvert.exporters.latex import LatexExporter

from .base import Template
from .html import HtmlTemplate
from ..resources import data_dir
from ..browser import grab_images

MARKDOWN_REGEXES = (
    # (re.compile("\^"), '\\\\textasciicircum'),
    (re.compile("\ˆ"), '\\\\textasciicircum'), )


class LatexTemplate(Template):
  def process(self):
    """Convert the notebook into latex"""
    self.bundle.prepare()

    latex_filename = self.bundle.complete_latex_filename()

    HtmlTemplate(self.bundle).process()    # Create the html file, if necessary
    images = grab_images(self.bundle.complete_html_filename(),
                         '#content-images img', self.bundle.build_dir)

    # self.to_html()    # Needed to create snapshots
    # snapshots = self.create_snapshots()
    output_tex = run_to_latex(self.bundle, latex_filename, images)

    return output_tex


def pretty_markdown(text, **kwargs):
  for p, replacement in MARKDOWN_REGEXES:
    text = p.sub(replacement, text)
  return text


@preserve_cwd
def run_to_latex(bundle, output_filename, snapshots):

  processed_file = bundle.merged_notebook
  title = bundle.title
  working_directory = bundle.working_directory
  template = bundle.template
  virtualenv_name = bundle.virtualenv_name

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
  print(snapshots)
  for x, cell in enumerate(nb.cells):
    new_cell = cell
    if cell['cell_type'] == 'code':
      # print(cell)
      # pass
      if 'outputs' in cell and len(cell['outputs']) > 0:
        pass
        # TODO: Fix this for only non-image outputs
        # with open(snapshots[i], 'rb') as f:
        #   new_cell.outputs = [
        #       nbformat.v4.new_output('display_data', {
        #           'image/png': base64.b64encode(f.read())
        #       })
        #   ]
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

  print(' '.join(args))

  output = execute_in_virtualenv(args, virtualenv_name)

  return output
