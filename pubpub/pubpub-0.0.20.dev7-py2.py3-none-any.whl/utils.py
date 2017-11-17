import os
from subprocess import Popen, PIPE, check_call, check_output
import pip
import logging
import re
import frontmatter
from jinja2 import Template

packages = pip.utils.get_installed_distributions()
package = packages[-1]

# First create the treeprocessor

LOCAL_IMAGES = re.compile('^\.\.\/assets')


def copyfile(src, dst):
  try:
    fin = os.open(src, READ_FLAGS)
    stat = os.fstat(fin)
    fout = os.open(dst, WRITE_FLAGS, stat.st_mode)
    for x in iter(lambda: os.read(fin, BUFFER_SIZE), ""):
      os.write(fout, x)
  finally:
    try:
      os.close(fin)
    except:
      pass
    try:
      os.close(fout)
    except:
      pass


def copytree(src, dst, symlinks=False, ignore=[]):
  names = os.listdir(src)

  if not os.path.exists(dst):
    os.makedirs(dst)
  errors = []
  for name in names:
    if name in ignore:
      continue
    srcname = os.path.join(src, name)
    dstname = os.path.join(dst, name)
    try:
      if symlinks and os.path.islink(srcname):
        linkto = os.readlink(srcname)
        os.symlink(linkto, dstname)
      elif os.path.isdir(srcname):
        copytree(srcname, dstname, symlinks, ignore)
      else:
        copyfile(srcname, dstname)
      # XXX What about devices, sockets etc.?
    except (IOError, os.error) as why:
      errors.append((srcname, dstname, str(why)))
    except CTError as err:
      errors.extend(err.errors)
  if errors:
    raise CTError(errors)


def preserve_cwd(function):
  def decorator(*args, **kwargs):
    cwd = os.getcwd()
    result = function(*args, **kwargs)
    os.chdir(cwd)
    return result

  return decorator


def setup_logging(count):
  level = 0
  if count == 1:
    level = logging.DEBUG
  elif count == 2:
    level = logging.INFO
  elif count == 3:
    level = logging.WARNING
  return setup_custom_logger('root', level)


def setup_custom_logger(name, level=0):
  formatter = logging.Formatter(
      fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

  handler = logging.StreamHandler()
  handler.setFormatter(formatter)

  logger = logging.getLogger(name)
  logger.setLevel(level)
  logger.addHandler(handler)
  return logger


def get_working_directory(file, build_dir=os.getcwd()):
  if file is not None:
    if os.path.isabs(file):
      return file
    else:
      filepath = os.path.abspath(os.path.join(build_dir, file))
      return filepath
  else:
    return build_dir


def create_template(tpl_file):
  return Template()


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


def execute_in_virtualenv(args, virtualenv_name=None):
  '''Execute Python code in a virtualenv, return its stdout and stderr.'''
  command = '/bin/bash'
  process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

  if virtualenv_name is not None:
    args = ['source', 'activate', virtualenv_name, '&&'] + args
  else:
    args = args

  args = ' '.join(args)

  logging.getLogger('root').debug('Running: %s' % args.encode('utf-8'))
  (output, err) = process.communicate(args.encode('utf-8'))
  resp = process.wait()

  if resp != 0:
    print("There was an error")
    print(args.encode('utf-8'))
    print(output)
    print(err)

  return output
