#!/usr/bin/env python

from __future__ import absolute_import
import boto3, clip, gzip, logging, logtool, os, progressbar
import retryp, shutil, threading, urlparse
from collections import namedtuple
from .linestream import linestream
from .rotatingfile_ctx import RotatingFile_Ctx

LOG = logging.getLogger (__name__)

class _ProgressPercentage (object):

  # pylint: disable=too-few-public-methods

  @logtool.log_call
  def __init__ (self, filename, quiet):
    self._filename = filename
    self._size = float (os.path.getsize (filename))
    self._lock = threading.Lock ()
    self.quiet = quiet
    self.progress = (progressbar.ProgressBar (max_value = self._size)
                     if not quiet else None)

  @logtool.log_call
  def __enter__ (self):
    return self

  @logtool.log_call
  def __exit__ (self, *args):
    if not self.quiet:
      self.progress.finish ()

  @logtool.log_call
  def __call__ (self, bytes_amount):
    if self.progress:
      with self._lock:
        self.progress.update (bytes_amount)

class Action (object):

  @logtool.log_call
  def __init__ (self, args):
    self.args = args
    self.p_from = self._parse_url ("Source", args.url_from)
    self.p_to = self._parse_url ("Destination", args.url_to)
    self.compress = args.compress
    self.check = args.check
    self.s3 = boto3.resource ("s3")
    self.keys = None

  @logtool.log_call
  def _parse_url (self, typ, url):
    _urlspec = namedtuple ("_UrlSpec", ["protocol", "bucket", "key"])
    p = urlparse.urlparse (url)
    rc = _urlspec (protocol = p.scheme, bucket = p.netloc,
                   key = p.path[1:] if p.path.startswith ("/") else p.path)
    if rc.protocol != "s3":
      print "%s protocol is not s3: %s" % (typ, url)
      clip.exit (err = True)
    return rc

  @retryp.retryp (expose_last_exc = True, log_faults = True)
  @logtool.log_call
  def _cleanup (self):
    if self.args.delete:
      if not self.args.quiet:
        print "Deleting..."
      for key in (progressbar.ProgressBar () (self.keys)
                  if not self.args.quiet else self.keys):
        key.delete ()

  @retryp.retryp (expose_last_exc = True, log_faults = True)
  @logtool.log_call
  def _send (self, ndx, fname):
    client = boto3.client("s3")
    out_f = self.p_to.key.format (ndx)
    if not self.args.quiet:
      print out_f
    if self.args.compress:
      with open(fname, "rb") as f_in, \
           gzip.open (fname + ".gz", "wb") as f_out:
        shutil.copyfileobj (f_in, f_out)
      fname = fname + ".gz"
    client.upload_file (fname, self.p_to.bucket, out_f)
    if self.args.compress:
      os.unlink (fname)

  @retryp.retryp (expose_last_exc = True, log_faults = True)
  @logtool.log_call
  def _list_from (self):
    bucket = self.s3.Bucket (self.p_from.bucket)
    self.keys = [k for k in bucket.objects.filter (
      Prefix = self.p_from.key)]

  @logtool.log_call
  def _pipedata (self):
    if not self.args.quiet:
      print "Streaming inputs..."
    progress = (progressbar.ProgressBar (max_value = len (self.keys),
                                         redirect_stdout = True)
                if not self.args.quiet else None)
    with RotatingFile_Ctx (self._send, block = int (self.args.block)) as rf:
      for line in linestream (self.keys,
                              cb = (progress.update if progress else None),
                              validate = self.args.json):
        rf.write (line)
    if progress:
      progress.finish ()

  @logtool.log_call
  def run (self):
    self._list_from ()
    self._pipedata ()
    self._cleanup ()
    if not self.args.quiet:
      print ""
