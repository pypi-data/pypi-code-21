import os
import pip
import logging
from pubpub.src.log import setup_custom_logger
import re

packages = pip.utils.get_installed_distributions()
package = packages[-1]

import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

# First create the treeprocessor

LOCAL_IMAGES = re.compile('^\.\.\/assets')


class ImgExtractor(Treeprocessor):
  def run(self, doc):
    "Find all images and append to markdown.images. "
    self.markdown.images = []
    for image in doc.findall('.//img'):
      src = image.attrib.get('src')
      if src and LOCAL_IMAGES.match(src):
        self.markdown.images.append(image.get('src'))


# Then tell markdown about it


class ImgExtExtension(Extension):
  def extendMarkdown(self, md, md_globals):
    img_ext = ImgExtractor(md)
    md.treeprocessors.add('imgext', img_ext, '>inline')


def markdown_instance():
  return markdown.Markdown(extensions=[ImgExtExtension()])


class CTError(Exception):
  def __init__(self, errors):
    self.errors = errors


try:
  O_BINARY = os.O_BINARY
except:
  O_BINARY = 0
READ_FLAGS = os.O_RDONLY | O_BINARY
WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
BUFFER_SIZE = 128 * 1024


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


def get_working_directory(file, build_dir=os.getcwd()):
  if file is not None:
    if os.path.isabs(file):
      return file
    else:
      filepath = os.path.abspath(os.path.join(build_dir, file))
      return filepath
  else:
    return build_dir
