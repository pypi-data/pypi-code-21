# This file is part of caucase
# Copyright (C) 2017  Nexedi
#     Alain Takoudjou <alain.takoudjou@nexedi.com>
#     Vincent Pelletier <vincent@nexedi.com>
#
# caucase is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caucase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caucase.  If not, see <http://www.gnu.org/licenses/>.
"""
Base WSGI-related classes for caucase HTTP(S) server.

Separate from .http because of different-licensed code in the middle.
"""
from __future__ import absolute_import
from wsgiref.simple_server import ServerHandler

class ProxyFile(object):
  """
  Passes any non-overridden calls to the actual_file object.
  """
  def __init__(self, actual_file):
    self._actual_file = actual_file

  def __getattr__(self, name):
    return getattr(self._actual_file, name)

MAX_CHUNKED_HEADER_LENGTH = 64 * 1024
class ChunkedFile(ProxyFile):
  """
  Implement chunked-encoding.
  """
  _at_eof = False

  def __init__(self, actual_file):
    super(ChunkedFile, self).__init__(actual_file)
    self._chunk_remaining_length = 0

  def read(self, length=None):
    """
    Read chunked data.
    """
    result = ''
    if not self._at_eof:
      readline = self.readline
      read = self.__getattr__('read')
      while True:
        if self._chunk_remaining_length:
          chunk_length = self._chunk_remaining_length
          self._chunk_remaining_length = 0
        else:
          chunk_header = readline(MAX_CHUNKED_HEADER_LENGTH + 1)
          if len(chunk_header) > MAX_CHUNKED_HEADER_LENGTH:
            raise ValueError('Chunked encoding header too long')
          try:
            chunk_length = int(chunk_header.split(';', 1)[0], 16)
          except ValueError:
            raise ValueError('Invalid chunked encoding header')
          if not chunk_length:
            trailer = readline(MAX_CHUNKED_HEADER_LENGTH + 1)
            if len(trailer) > MAX_CHUNKED_HEADER_LENGTH:
              raise ValueError('Chunked encoding trailer too long')
            self._at_eof = True
            break
        if length is None:
          to_read = chunk_length
        else:
          to_read = min(chunk_length, length - len(result))
        result += read(to_read)
        if to_read != chunk_length:
          self._chunk_remaining_length = chunk_length - to_read
          break
        if read(2) != '\r\n':
          raise ValueError('Invalid chunked encoding separator')
    return result

class HookFirstReadFile(ProxyFile):
  """
  Trigger a callable on first read.
  """
  def __init__(self, actual_file, on_first_read):
    super(HookFirstReadFile, self).__init__(actual_file)
    self._on_first_read = on_first_read
    self.read = self._read_hook

  def _read_hook(self, *args, **kw):
    self._on_first_read()
    del self.read
    return self.read(*args, **kw)

class CleanServerHandler(ServerHandler):
  """
  - Handle chunked transfer encoding.
  - Handle expect/continue protocol.
  - Do not include OS environment variables in each request's WSGI environment.
    Seriously, what the fsck, python ?
  """
  os_environ = {}

  def setup_environ(self):
    ServerHandler.setup_environ(self)
    environ = self.environ
    request_major, request_minor = environ[
      'SERVER_PROTOCOL'
    ].upper().split('/', 1)[1].split('.', 1)
    request_version = (int(request_major), int(request_minor))
    if request_version > (1, 0):
      if environ.get('HTTP_TRANSFER_ENCODING', '').lower() == 'chunked':
        # XXX: does not support multiple encodings specified at once
        # (ex: chunked + gzip).
        # We handle this, hide it from Application
        del environ['HTTP_TRANSFER_ENCODING']
        environ['wsgi.input'] = ChunkedFile(environ['wsgi.input'])
      if environ.get('HTTP_EXPECT', '').lower() == '100-continue':
        # We handle this, hide it from Application
        del environ['HTTP_EXPECT']
        environ['wsgi.input'] = HookFirstReadFile(
          environ['wsgi.input'],
          self._100_continue,
        )

  def _100_continue(self):
    """
    Emit "100 Continue" intermediate response.
    """
    self._write('HTTP/%s 100 Continue\r\n\r\n' % (
      self.http_version,
    ))
    self._flush()
