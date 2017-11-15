from os import path
import hashlib
import os
import io
import logging
import re
import glob
import json
import tempfile
import nbformat
from subprocess import Popen, PIPE, check_call, check_output
from distutils.dir_util import copy_tree
import atexit
import sys
import shutil
from .utils import preserve_cwd


class Printer(object):
  def __init__(self, **kwargs):
    self.debug = kwargs.get('debug', 0)
    level = 0
    if self.debug == 1:
      level = logging.DEBUG
    elif self.debug == 2:
      level = logging.INFO
    logging.basicConfig(format='%(asctime)s %(message)s', level=level)

    output = kwargs.get('output', '/tmp/output.pdf')
    build_dir = path.join(path.dirname(path.realpath(output)), 'build_dir/')
    self.build_dir = self.get_working_directory(build_dir)

    self.output = self.get_working_directory(
        kwargs.get('output', '/tmp/output.pdf'))
    self.directory = self.get_working_directory(kwargs.get('directory'))
    self.virtualenv_name = kwargs.get('virtualenv_name')
    self.chapters_list_file = kwargs.get('chapter_list_file',
                                         self.build_dir + 'chapters.txt')

    wd = self.get_working_directory(
        kwargs.get('working_directory', self.build_dir))
    if wd is None:
      wd = self.build_dir

    self.working_directory = wd

    files = kwargs.get('files', [])
    if not files and self.directory is not None:
      files = glob.glob(self.directory)

    self.files = []
    for i, filename in enumerate(files):
      self.files.append(
          self.get_working_directory(filename, self.working_directory))

    self.template = self.get_working_directory(kwargs.get('template'))

    logging.debug("""
  build_dir: %s
  template: %s
  output: %s
  working dir: %s
    """ % (self.build_dir, self.template, self.output, self.working_directory))
    # self.config_file = kwargs.get('config')

  @preserve_cwd
  def build_notebooks(self, **kwargs):
    '''build notebooks'''

    # build_dir = path.dirname(self.output) + '/build_dir/'
    self.make_dirs()
    os.chdir(self.working_directory)
    logging.debug("Working in directory: %s" % os.getcwd())
    chapters = self.process_notebooks()

    chapters_list_file = self.build_dir + 'chapters.txt'
    with open(chapters_list_file, 'w') as output:
      for filepath in chapters:
        entry = "{}\n".format(filepath)
        print(entry)
        output.write(entry)

    return chapters_list_file

  @preserve_cwd
  def pdf(self, **kwargs):
    '''main function'''

    chapters_list_file = self.build_dir + 'chapters.txt'
    if not path.exists(chapters_list_file):
      self.build_notebooks(**kwargs)

    with open(chapters_list_file, 'r') as f:
      lines = f.readlines()

    for line in lines:
      # out = self.pdflatex(line)
      out = self.create_pdf(line)
      print(out)
    # curr_dir = os.getcwd()
    # # atexit.register(self.cleanup)

    # # build_dir = path.dirname(self.output) + '/build_dir/'
    # self.make_dirs()
    # os.chdir(self.working_directory)
    # logging.debug("Working in directory: %s" % os.getcwd())
    # chapters = self.process_notebooks()

    # # merged_filename = self.merge_notebooks(chapters)

    # # logging.debug("Merged filename: %s" % merged_filename)
    # # output = self.create_pdf(merged_filename)
    # os.chdir(curr_dir)
    # # self.cleanup()

  def get_working_directory(self, from_dir, build_dir=os.getcwd()):
    if from_dir is not None:
      if path.isabs(from_dir):
        return from_dir
      else:
        filepath = path.abspath(path.join(build_dir, from_dir))
        return filepath

  def make_dirs(self):
    '''Make the required directories'''
    if not path.exists(self.build_dir):
      logging.debug("Creating build_dir: %s" % self.build_dir)
      os.makedirs(self.build_dir)

  def process_notebooks(self):
    chapters = []
    for i, filename in enumerate(self.files):
      if filename == self.output:
        continue

      logging.debug("Including file: %s" % filename)
      chapter_output = self.process_notebook(filename, i)

      chapters.append(chapter_output)
    return chapters

  def process_notebook(self, filename, i=0):
    '''Process a single notebook'''
    with open(filename, 'r') as source:
      lines = source.readlines()

    basename = str(i).zfill(2)
    pynb_filename = self.build_dir + basename + '.ipynb'
    tex_filename = self.build_dir + basename + '.tex'
    pdf_filename = self.build_dir + basename + '.pdf'
    md_filename = self.build_dir + basename + '.md'

    with open(tex_filename, 'w') as output:
      for line in lines:
        output.write(line)

    self.run_nbconvert(filename, pynb_filename)
    logging.debug("After nbconvert %s" % md_filename)
    self.to_markdown(pynb_filename, md_filename)
    # self.to_latex(pynb_filename, tex_filename)
    # self.clean_latex(tex_filename)

    return md_filename
    # self.pdflatex(tex_filename)

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
    with open(output_filename, 'w') as f:
      f.write(nbformat.writes(merged))
    return output_filename

  def write_to_tempfile(self, merged):
    '''Write the merged notebook to a tempfile'''
    f = tempfile.NamedTemporaryFile(delete=False, dir=os.getcwd())
    f.write(merged.encode('utf-8'))
    f.close()
    self.tempfile = f
    return f

  @preserve_cwd
  def run_nbconvert(self, processed_file, output_filename):
    args = [
        'jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--output',
        output_filename,
        "\"%s\"" % processed_file
    ]

    os.chdir(self.working_directory)

    return self.execute_in_virtualenv(args)

  @preserve_cwd
  def to_latex(self, processed_file, output_filename):
    args = [
        'jupyter', 'nbconvert', '--to', 'latex', '--output', output_filename,
        '--template', self.template,
        "\"%s\"" % processed_file
    ]

    os.chdir(self.working_directory)
    return self.execute_in_virtualenv(args)

  @preserve_cwd
  def to_markdown(self, processed_file, output_filename):
    args = [
        'jupyter',
        'nbconvert',
        '--to',
        'markdown',
        '--output',
        output_filename,    #'--template', self.template,
        "\"%s\"" % processed_file
    ]

    os.chdir(self.working_directory)
    return self.execute_in_virtualenv(args)

  @preserve_cwd
  def to_pdf(self, processed_file, output_filename):
    args = [
        'jupyter', 'nbconvert', '--to', 'pdf', '--output', output_filename,
        "\"%s\"" % processed_file
    ]

    print(' '.join(args))

    os.chdir(self.working_directory)
    return self.execute_in_virtualenv(args)

  def execute_in_virtualenv(self, args):
    '''Execute Python code in a virtualenv, return its stdout and stderr.'''
    command = '/bin/bash'
    process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

    if self.virtualenv_name is not None:
      args = ['source', 'activate', self.virtualenv_name, '&&'] + args
    else:
      args = args

    args = ' '.join(args)
    (output, err) = process.communicate(args.encode('utf-8'))
    process.wait()
    return output

  def clean_latex(self, tex_filename):
    '''clean up the latex file'''
    with open(tex_filename, 'r') as texfile:
      tex = texfile.read()

    # tex = re.sub(
    #     "\\\section\{.*?\}", "", tex,
    #     flags=re.DOTALL)    # Delete all sections (would be duplicate)
    # tex = re.sub("\\\subsection\{(\d+\. )?", "\\\chapter{",
    #              tex)    # rename numbered subsections to chapters
    # tex = re.sub("\\\documentclass\{.*?\}", "\\\documentclass{article}",
    #              tex)    # change documentclass to report
    # tex = re.sub("\\\maketitle", "\\\\tableofcontents",
    #              tex)    # include tableof

    with open(tex_filename, 'w') as texfile:
      texfile.writelines(tex)

  @preserve_cwd
  def pdflatex(self, tex_filename):
    '''convert to pdf'''
    os.chdir(self.working_directory)

    texbasename = os.path.join(
        os.path.dirname(tex_filename),
        os.path.splitext(os.path.basename(tex_filename))[0])

    def _run_pdflatex():
      args = [
          "pdflatex", "-interaction=nonstopmode",
          "-output-directory=%s" % self.build_dir, tex_filename
      ]
      self.execute_in_virtualenv(args)

    def _run_bibtex():
      args = [
          "bibtex", "-interaction=nonstopmode",
          "-output-directory=%s" % self.build_dir, texbasename + ".aux"
      ]
      self.execute_in_virtualenv(args)

    try:
      _run_pdflatex()
      _run_bibtex()
      _run_pdflatex()
      _run_pdflatex()
      return texbasename + ".pdf"
    except Exception as ex:
      print(ex)
      raise ex

  def move_file_to_output(self, from_file):
    logging.debug("Moving %s to %s" % (from_file, self.output))
    if os.path.exists(self.output):
      os.remove(self.output)
    return shutil.move(from_file, self.output)

  def create_pdf(self, filename):
    basename = os.path.splitext(os.path.basename(filename))[0]
    tex_filename = path.join(self.build_dir, 'merged.tex')
    pdf_filename = path.join(self.build_dir, basename + '.pdf')

    out = self.to_pdf(filename, pdf_filename)
    return out

  # def create_pdf_from_filename(self, filename):

  # self.to_latex(filename, tex_filename)
  # self.clean_latex(tex_filename)

  # self.pdflatex(tex_filename)
  # return self.move_file_to_output(pdf_filename)

  def cleanup(self):
    '''remove the temporary file'''
    if not self.debug > 0 and self.build_dir is not None:
      logging.debug("Cleaning up build dir: %s" % self.build_dir)
      shutil.rmtree(self.build_dir)
