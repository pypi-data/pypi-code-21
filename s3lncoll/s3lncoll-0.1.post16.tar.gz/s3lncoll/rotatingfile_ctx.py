#! /usr/bin/env python

import logtool, tempfile

class RotatingFile_Ctx (object):

  @logtool.log_call
  def __init__ (self, cb, block = 1024, start = 0):
    self.cb = cb
    self.block = block
    self.count = start
    self.fh = None
    self.length = 0

  @logtool.log_call
  def _file_done (self):
    if self.fh is not None:
      self.fh.close ()
      self.count += 1
      self.cb (self.count, self.fh.name)
      self.fh.unlink (self.fh.name)
      self.fh = None
    self.fh = tempfile.NamedTemporaryFile (
      prefix = "s3lncoll__", delete = False)
    self.length = 0

  @logtool.log_call
  def write (self, data):
    if self.fh is None or (self.length != 0
                           and self.length + len (data) > self.block):
      self._file_done ()
    self.fh.write (data)
    self.length += len (data)
    return self.length

  @logtool.log_call
  def __enter__ (self):
    return self

  @logtool.log_call
  def __exit__ (self, *_):
    if self.fh is not None:
      self._file_done ()
