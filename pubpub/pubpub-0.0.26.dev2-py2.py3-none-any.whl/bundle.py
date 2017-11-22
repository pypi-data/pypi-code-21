import logging, os
from .utils import get_working_directory, to_absolute_path, to_absolute_paths


class Bundle():
  def __init__(self, **opts):
    logger = logging.getLogger('root')

    opts['output'] = to_absolute_path(opts['output'])
    opts['base_dir'] = to_absolute_path(opts['base_dir'])
    opts['directory'] = to_absolute_path(opts['directory'])
    opts['input_file'] = to_absolute_paths(opts['input_file'])
    opts['working_directory'] = to_absolute_path(opts['working_directory'])
    opts['cover_image'] = to_absolute_path(opts['cover_image'])
    opts['cover_pdf'] = to_absolute_path(opts['cover_pdf'])
    opts['file'] = to_absolute_path(opts['file'])
    opts['asset_files'] = to_absolute_paths(opts['asset_files'])

    output = opts.get('output', '/tmp/output.pdf')

    # Setup build dir
    # output = kwargs.get('output', '/tmp/output.pdf')
    self.output = output
    self.output_basename = os.path.join(
        os.path.dirname(output),
        os.path.basename(output).split(".")[0])

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
