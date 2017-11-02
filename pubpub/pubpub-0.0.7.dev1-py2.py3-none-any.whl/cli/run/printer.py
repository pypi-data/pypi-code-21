from os import path, unlink, environ, chdir, getcwd, makedirs
import io
import logging
import re
import glob
import json
import tempfile
import nbformat
from subprocess import Popen, PIPE, check_call
from distutils.dir_util import copy_tree
import sys
import shutil


class Printer(object):
  def __init__(self, **kwargs):
    self.debug = debug = kwargs.get('debug', 0)
    level = debug * 10
    logging.basicConfig(format='%(asctime)s %(message)s', level=level)

    output = kwargs.get('output', '/tmp/output.pdf')
    build_dir = path.join(path.dirname(path.realpath(output)), 'build_dir/')
    self.build_dir = self.get_working_directory(build_dir)

    self.output = self.get_working_directory(kwargs.get('output', '/tmp'))
    self.directory = self.get_working_directory(kwargs.get('directory'))
    self.virtualenv_name = kwargs.get('virtualenv_name', 'udeeply')

    files = kwargs.get('files', [])
    if not files:
      files = glob.glob(self.directory)

    self.files = []
    for i, filename in enumerate(files):
      self.files.append(self.get_working_directory(filename))

    self.copy_files = kwargs.get('copy', [])
    self.working_dir = self.get_working_directory(
        kwargs.get('working_dir', '/tmp'))
    self.template = self.get_working_directory(kwargs.get('template'))

    logging.info("""
  build_dir: %s
  working_dir: %s
  template: %s
    """ % (self.build_dir, self.working_dir, self.template))
    # self.config_file = kwargs.get('config')

  def run(self, **kwargs):
    '''main function'''
    curr_dir = getcwd()
    try:
      # build_dir = path.dirname(self.output) + '/build_dir/'
      self.make_dirs()
      chdir(self.build_dir)
      chapters = self.process_notebooks()
      merged_filename = self.merge_notebooks(chapters)

      logging.info("Merged filename: %s" % merged_filename)
      self.create_pdf(merged_filename)

      # self.join_pdfs(chapters)
      # file = self.write_to_tempfile(merged)
      # self.copy_linked_files()
      # output = self.run_nbconvert(file.name)
      # self.clean_latex(file.name)
      # self.pdflatex(file.name)
    finally:
      chdir(curr_dir)
      self.cleanup()

  def get_working_directory(self, from_dir):
    build_dir = getcwd()
    if from_dir is not None:
      if path.isabs(from_dir):
        return from_dir
      else:
        filepath = path.abspath(path.join(build_dir, from_dir))
        return filepath

  def make_dirs(self):
    '''Make the required directories'''
    if not path.exists(self.build_dir):
      logging.info("Creating build_dir: %s" % self.build_dir)
      makedirs(self.build_dir)

  def process_notebooks(self):
    chapters = []
    for i, filename in enumerate(self.files):
      if filename == self.output:
        continue

      logging.info("Including file: %s" % filename)

      with open(filename, 'r') as source:
        lines = source.readlines()

      output_filename = str(i).zfill(2) + '.ipynb'
      with open(output_filename, 'w') as output:
        for line in lines:
          output.write(line)

      self.run_nbconvert(filename, output_filename)
      # tex_filename = self.build_dir + str(i) + '.tex'
      # self.to_latex(self.build_dir + output_filename, tex_filename)

      # self.clean_latex(tex_filename)
      # self.pdflatex(tex_filename)
      # pdf_filename = self.build_dir + str(i) + '.pdf'
      chapters.append(output_filename)
    return chapters

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
    f = tempfile.NamedTemporaryFile(delete=False, dir=getcwd())
    f.write(merged.encode('utf-8'))
    f.close()
    self.tempfile = f
    return f

  def copy_linked_files(self):
    '''copy linked files into the build directory'''
    for file in self.copy_files:
      copy_tree(file, self.build_dir)

  def run_nbconvert(self, processed_file, output_filename):
    jupyter_args = [
        'jupyter', 'nbconvert', '--execute', '--to', 'notebook', '--output',
        output_filename,
        "\"%s\"" % processed_file
    ]
    if self.virtualenv_name is not None:
      args = ['source', 'activate', self.virtualenv_name, '&&'] + jupyter_args
    else:
      args = jupyter_args

    command = ' '.join(args)
    return self.execute_in_virtualenv(command)

  def to_latex(self, processed_file, output_filename):
    args = [
        'jupyter', 'nbconvert', '--to', 'latex', '--output', output_filename,
        '--template', self.template,
        "\"%s\"" % processed_file
    ]

    command = ' '.join(args)
    return self.execute_in_virtualenv(command)

  def execute_in_virtualenv(self, commands):
    '''Execute Python code in a virtualenv, return its stdout and stderr.'''
    command = '/bin/bash'
    process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    (output, err) = process.communicate(commands.encode('utf-8'))
    print(err)
    return output

  def clean_latex(self, tex_filename):
    '''clean up the latex file'''
    with open(tex_filename, 'r') as texfile:
      tex = texfile.read()

    # tex = re.sub(
    # "\\\section\{.*?\}", "", tex,
    # flags=re.DOTALL)    # Delete all sections (would be duplicate)
    # tex = re.sub("\\\subsection\{(\d+\. )?", "\\\chapter{",
    #  tex)    # rename numbered subsections to chapters
    # tex = re.sub("\\\documentclass\{.*?\}", "\\\documentclass{article}",
    #  tex)    # change documentclass to report
    # tex = re.sub("\\\maketitle", "\\\\tableofcontents",
    #  tex)    # include tableof

    with open(tex_filename, 'w') as texfile:
      texfile.writelines(tex)

  def pdflatex(self, tex_filename):
    '''convert to pdf'''
    logging.info(
        "pdf from latex: pdflatex -interaction=nonstopmode %s" % tex_filename)
    check_call(
        "pdflatex -interaction=nonstopmode %s" % tex_filename, shell=True)

  def move_file_to_output(self, from_file):
    logging.info("Moving %s to %s" % (from_file, self.output))
    shutil.move(from_file, self.output)

  def create_pdf(self, filename):
    tex_filename = path.join(self.build_dir, 'merged.tex')
    pdf_filename = path.join(self.build_dir, 'merged.pdf')

    self.to_latex(filename, tex_filename)
    self.clean_latex(tex_filename)

    self.pdflatex(tex_filename)
    self.move_file_to_output(pdf_filename)

  def join_pdfs(self, chapters):
    args = [
        'pdfjoin', '--paper', 'a4paper', '--no-landscape', '--twoside',
        '--rotateoversize', 'false', '--outfile', self.output
    ]
    for chapter in chapters:
      args.append(chapter)

    command = ' '.join(args)
    logging.info("Executing in virtual env: %s" % command)
    return self.execute_in_virtualenv(command)

  def cleanup(self):
    '''remove the temporary file'''
    logging.info("Cleaning up build dir: %s" % self.build_dir)
    if self.debug != 0:
      shutil.rmtree(self.build_dir)
