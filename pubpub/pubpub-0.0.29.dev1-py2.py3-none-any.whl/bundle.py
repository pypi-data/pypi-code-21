import logging, os, io
import nbformat, shutil
from .utils import get_working_directory, to_absolute_path, to_absolute_paths, preserve_cwd, execute_in_virtualenv
from .resources import read_html, compiled_scss, empty_notebook_path, create_template


class Bundle():
  def __init__(self, **opts):
    logger = logging.getLogger('root')

    opts['output'] = to_absolute_path(opts['output'])
    self.base_dir = opts['base_dir'] = to_absolute_path(opts['base_dir'])

    opts['directory'] = to_absolute_path(opts['directory'], self.base_dir)
    opts['input_file'] = to_absolute_paths(opts['input_file'], self.base_dir)
    opts['working_directory'] = to_absolute_path(opts['working_directory'],
                                                 self.base_dir)
    opts['cover_image'] = to_absolute_path(opts['cover_image'], self.base_dir)
    opts['cover_pdf'] = to_absolute_path(opts['cover_pdf'], self.base_dir)
    opts['file'] = to_absolute_path(opts['file'], self.base_dir)
    opts['asset_files'] = to_absolute_paths(opts['asset_files'], self.base_dir)
    opts['template'] = to_absolute_path(opts['template'], self.base_dir)

    output = opts.get('output', '/tmp/output.pdf')

    # Setup build dir
    # output = kwargs.get('output', '/tmp/output.pdf')
    self.output = output
    self.output_basename = os.path.join(
        os.path.dirname(output), os.path.basename(output).split(".")[0])

    self.build_dir = os.path.join(
        os.path.dirname(os.path.realpath(output)), 'build_dir/')

    self.make_dir()

    opts['template'] = self.prepare_template(opts.get('template'), **opts)

    self.title = opts.get('title', 'Some title')
    self.virtualenv_name = opts.get('virtualenv')
    self.base_dir = opts.get('base_dir', self.build_dir)
    self.working_directory = get_working_directory(
        opts.get('working_directory'), self.base_dir)
    self.template = opts.get('template')

    self.authors = opts.get('authors', [])
    self.asset_files = opts.get('asset_files', [])
    self.cover_image = opts.get('cover_image')

    self.kernelspec = opts.get('kernel_spec')

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

  # ACCESSORS
  def complete_html_filename(self):
    return os.path.join(self.build_dir, "complete.html")

  def complete_latex_filename(self):
    return os.path.join(self.build_dir, 'complete.tex')

  def prepare(self):
    '''Prepare for running'''
    for i, (src, d) in enumerate(self.files_for_processing.items()):
      if not os.path.exists(d['pynb']):
        self.run_to_notebook(src, d['pynb'])

    self.merged_notebook = self.merge_notebooks(
        [x['pynb'] for (src, x) in self.files_for_processing.items()])

    self.copy_assets()

    return self.files_for_processing

  def prepare_template(self, template_file, **opts):
    if template_file is not None:
      tpl = create_template(template_file, **opts)

      template_ext = template_file.split('.')[-1]
      rendered_template_file = self.build_dir + 'rendered-template.' + template_ext

      with open(rendered_template_file, 'w') as f:
        f.write(tpl)

      return rendered_template_file
    else:
      return template_file

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

  def make_dir(self, directory=None):
    '''Make the required directories'''
    if directory is None:
      directory = self.build_dir
    if not os.path.exists(directory):
      logging.debug("Creating build_dir: %s" % directory)
      os.makedirs(directory)

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
      tofilepath = os.path.join(self.build_dir, os.path.basename(tofile))
      logging.getLogger('root').info(("Copying %s to %s" % (filepath,
                                                            tofilepath)))

      if not os.path.exists(tofilepath):
        shutil.copytree(filepath, tofilepath)
      copied_assets.append(tofilepath)
    return copied_assets

  def clean_notebook(self, notebook_file):
    try:
      with open(notebook_file, "r") as f:
        nb = nbformat.reads(f.read(), as_version=4)

        if self.kernelspec is not None:
          nb.metadata['kernelspec'] = self.kernelspec

        nbformat.write(nb, f)
    except:
      pass

  @preserve_cwd
  def run_to_notebook(self, processed_file, output_filename):
    self.clean_notebook(processed_file)

    config_file = os.path.join(os.path.dirname(__file__), 'config.py')
    args = [
        'jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--output',
        output_filename,
        "\"%s\"" % processed_file
    ]

    os.chdir(self.working_directory)

    logging.getLogger('root').debug('executing: {}'.format(' '.join(args)))
    return execute_in_virtualenv(args, self.virtualenv_name)

  def rendered_template_file(self, template_file):
    template_ext = template_file.split('.')[-1]
    return self.build_dir + 'rendered-template.' + template_ext
