from __future__ import print_function
import os
import shutil
import logging
import re
import io
import nbformat
from bs4 import BeautifulSoup
from subprocess import Popen, PIPE, check_call, check_output
from .data import read_html, compiled_scss, empty_notebook_path
from .utils import get_working_directory, preserve_cwd, create_template, execute_in_virtualenv
from .browser import render_snapshots
from .runners.run_to_html import run_to_html
from .runners.run_to_latex import run_to_latex

# from .formatters import update_cells, update_tex

LOCAL_IMAGES = re.compile('^\.\.\/assets')


class Processor():
  def __init__(self, **opts):
    logger = logging.getLogger('root')

    output = opts.get('output', '/tmp/output.pdf')

    # Setup build dir
    # output = kwargs.get('output', '/tmp/output.pdf')
    self.output = output
    self.output_basename = os.path.join(
        os.path.dirname(output), os.path.basename(output).split(".")[0])

    self.build_dir = os.path.join(
        os.path.dirname(os.path.realpath(output)), 'build_dir/')

    self.title = opts.get('title', 'Some title')
    self.virtualenv_name = opts.get('virtualenv')
    self.base_dir = opts.get('base_dir', self.build_dir)
    self.working_directory = get_working_directory(
        opts.get('working_directory'), self.base_dir)
    self.template = opts.get('template')
    self.authors = opts.get('authors', [])
    self.asset_files = opts.get('asset_files', [])

    self.debug = opts.get('debug', 0)
    files = opts.get('files', [])

    logger.debug("""
    Book: {}
    Virtualenv: {}
    Authors: {}
    Template: {}
    ---

    Working directory: {}
    Build directory: {}
    Files: {}
    """.format(self.title, self.virtualenv_name, self.authors,
               get_working_directory(self.template, self.working_directory),
               self.build_dir, self.working_directory, files))

    self.files = []
    self.files_for_processing = {}
    for i, filename in enumerate(files):
      file = get_working_directory(filename, self.working_directory)
      self.files.append(file)

      ## Processing files
      basename = str(i).zfill(2)
      pynb_filename = self.build_dir + basename + '.ipynb'
      html_filename = self.build_dir + basename + '.html'
      tex_filename = self.build_dir + basename + '.tex'

      self.files_for_processing[file] = {
          'pynb': pynb_filename,
          'html': html_filename,
          'tex': tex_filename
      }

    logger.info("Files: {}".format(self.files))

    self.opts = opts

  def prepare(self):
    self.make_dir()
    for i, (src, d) in enumerate(self.files_for_processing.items()):
      if not os.path.exists(d['pynb']):
        self.run_to_notebook(src, d['pynb'])

    self.merged_notebook = self.merge_notebooks(
        [x['pynb'] for (src, x) in self.files_for_processing.items()])

    self.copy_assets()

    return self.files_for_processing

  def to_latex(self):
    """Convert the notebook into latex"""
    self.prepare()

    latex_filename = self.build_dir + 'complete.tex'

    opts = self.opts.copy()
    opts.update({
        'working_directory': self.working_directory,
        'build_dir': self.build_dir,
    })
    self.to_html()    # Needed to create snapshots
    snapshots = self.create_snapshots()
    output_tex = run_to_latex(self.merged_notebook, latex_filename, snapshots,
                              **opts)

    return output_tex

  def to_html(self):
    """Take the merged notebooks and turn it into HTML"""
    processing_files = self.prepare()
    output_content = []

    (body, resources) = run_to_html(self.merged_notebook)
    self.update_styles()

    complete_filename = os.path.join(self.build_dir, "complete.html")
    with io.open(complete_filename, "w") as f:
      f.write(body)

    return complete_filename

  def create_snapshots(self):
    """Take the rendered HTML and extract the outputs into images"""
    complete_filename = os.path.join(self.build_dir, "complete.html")
    return render_snapshots(complete_filename)

  def process_notebook_notebooks(self, filename, pynb_filename, i=0, **opts):
    self.run_to_notebook(filename, pynb_filename)

    return pynb_filename

  def merge_notebooks(self, chapters):
    '''Merge all the chapters together'''
    merged = None
    for filename in chapters:
      if filename == self.output:
        continue

      with io.open(filename, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

      if merged is None:
        merged = nb
      else:
        merged.cells.extend(nb.cells)

    if not hasattr(merged.metadata, 'name'):
      merged.metadata.name = ''

    merged.metadata.name += "_merged"

    output_filename = self.build_dir + "output-merged.ipynb"
    with io.open(output_filename, 'w') as f:
      f.write(nbformat.writes(merged))
    return output_filename

  @preserve_cwd
  def run_pdflatex(self, input_filename, output_filename):
    if input_filename is None or input_filename == []:
      input_filename = self.build_dir + 'complete.tex'

    output_dir = '/tmp'

    args = [
        'pdflatex',
        '-output-directory=%s' % output_dir, '-synctex=1',
        '-interaction=nonstopmode',
        '\"%s\"' % input_filename
    ]

    os.chdir(self.build_dir)
    execute_in_virtualenv(args, self.virtualenv_name)

    if output_filename != '/tmp/complete.pdf':
      shutil.move('/tmp/complete.pdf', output_filename)

    logging.getLogger('root').debug('Created: {}'.format(output_filename))
    return output_filename

  def update_styles(self):
    with io.open(self.build_dir + "custom.css", "w") as f:
      f.write(compiled_scss())

  def add_toc(self, html_content=None):
    if html_content is None:
      html_content = self.read_html_files()
    toc_filename = self.build_dir + "toc.html"
    output = []
    toc = ['<div class="table-of-contents contents">', '<ol>']

    for i, content in enumerate(html_content):
      toc.append('<li class="level-0">')
      soup = BeautifulSoup(content, "lxml")
      headers = soup.find_all(re.compile('^h[%d-3]' % 1))

      # first_header = headers[0]
      # headers = headers[1:-1]
      # toc.append(first_header.text)
      toc.append('<ol>')
      for header in headers:
        hid = header.get('id')
        text = header.text
        level = int(header.name[-1]) - 1
        if hid:
          # chapter_toc[level].append((hid, text))
          toc.append('<li class="level-%d"><a href="#%s">%s</a></li>' %
                     (level, hid, text))
      toc.append("</ol></li>")

    toc.append("</div>")
    toc = "".join(toc)
    with io.open(toc_filename, "w") as f:
      f.write(toc)
    return (toc_filename, toc)

  @preserve_cwd
  def run_to_notebook(self, processed_file, output_filename):
    args = [
        'jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--output',
        output_filename,
        "\"%s\"" % processed_file
    ]

    os.chdir(self.working_directory)

    logging.getLogger('root').debug('executing: {}'.format(' '.join(args)))
    return execute_in_virtualenv(args, self.virtualenv_name)

  @preserve_cwd
  def run_to_markdown(self, processed_file, output_filename):
    args = [
        'jupyter', 'nbconvert', '--to', 'markdown', '--template',
        self.template, '--output', output_filename,
        "\"%s\"" % processed_file
    ]

    os.chdir(self.working_directory)
    return execute_in_virtualenv(args, self.virtualenv_name)

  # @preserve_cwd
  # def run_to_latex(self, processed_file, output_filename):
  #   config_file = os.path.join(os.path.dirname(__file__), 'config.py')
  #   args = [
  #       'jupyter',
  #       'nbconvert',
  #       '--to',
  #       'latex',
  #       '--config %s' % config_file,
  #       '--output',
  #       output_filename,
  #   ]

  #   if self.template is not None:
  #     args.append('--template %s' % get_working_directory(
  #         self.template, self.working_directory))

  #   args.append("\"%s\"" % processed_file)

  #   os.chdir(self.working_directory)
  #   output = execute_in_virtualenv(args, self.virtualenv_name)

  #   return output

  @preserve_cwd
  def run_latex_to_pdf(self, processed_file, output_filename):
    args = [
        'pandoc', '-N', '--template=' + self.template, '--variable',
        'mainfont="Palatino"', '--variable', 'sansfont="Helvetica"',
        '--variable', 'monofont="Menlo"', '--variable', 'fontsize=12pt',
        '--variable', 'version=2.0', processed_file, '--from', 'latex',
        '--listings', '--toc', '-o', output_filename
    # pandoc example.md -o example.pdf --from markdown --template eisvogel --listings
    ]

    os.chdir(self.working_directory)
    return execute_in_virtualenv(args, self.virtualenv_name)

  def find_images_to_copy(self, html_body):
    markdown_images = []
    soup = BeautifulSoup(html_body, "lxml")
    for img in soup.find_all("img"):
      if not img.attrs.get('src', '').startswith('data:'):
        markdown_images.append(img.get('src'))
    return markdown_images

  def copy_images_assets(self, md_filename, src_file, dest_dir):
    assets = self.find_images_to_copy(md_filename)
    for file in assets:
      dest = os.path.join(dest_dir,
                          os.path.dirname(file), os.path.basename(file))

      src = get_working_directory(
          os.path.join(src_file, file), self.working_directory)

      self.make_dir(os.path.dirname(dest))
      # print(src, dest)
      logging.getLogger('root').info('Copying {} to {}'.format(src, dest))
      shutil.copyfile(src, dest)

  def copy_assets(self):
    """Copy assets"""
    copied_assets = []
    for file in self.asset_files:
      split = file.split(':')
      if len(split) == 2:
        (file, tofile) = split
      else:
        (file, tofile) = (file, file)

      filepath = os.path.abspath(os.path.join(self.base_dir, file))
      tofilepath = os.path.join(self.build_dir, tofile)
      logging.getLogger('root').info(("Copying %s to %s" % (filepath,
                                                            tofilepath)))
      if tofilepath is not None and os.path.exists(tofilepath):
        shutil.rmtree(tofilepath)
      shutil.copytree(filepath, tofilepath)
      copied_assets.append(tofilepath)
    return copied_assets

  def make_dir(self, directory=None):
    '''Make the required directories'''
    if directory is None:
      directory = self.build_dir
    if not os.path.exists(directory):
      logging.debug("Creating build_dir: %s" % directory)
      os.makedirs(directory)

  def cleanup(self):
    '''remove the temporary file'''
    if self.debug != 0:
      # Cleanup assets
      if self.copied_assets is not None:
        for file in self.copied_assets:
          if file is not None and file != '/':
            shutil.rmtree(file)
      # Cleanup build_dir
      if self.build_dir is not None and self.build_dir is not '' and self.build_dir is not '/':
        logging.debug("Cleaning up build dir: %s" % self.build_dir)
        shutil.rmtree(self.build_dir)

  def write_to_tempfile(self, content):
    '''Write the merged notebook to a tempfile'''
    f = tempfile.NamedTemporaryFile(delete=False, dir=os.getcwd())
    f.write(content.encode('utf-8'))
    f.close()
    self.tempfile = f
    return f
