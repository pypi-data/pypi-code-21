# -*- coding: utf-8 -*-
"""The LZMA and XZ decompressor implementations."""

from __future__ import unicode_literals

import sys

import lzma  # pylint: disable=wrong-import-order

# Different versions of lzma define LZMAError in different places.
# pylint: disable=no-name-in-module
try:
  from lzma import LZMAError
except ImportError:
  from lzma import error as LZMAError

from dfvfs.compression import decompressor
from dfvfs.compression import manager
from dfvfs.lib import definitions
from dfvfs.lib import errors


class XZDecompressor(decompressor.Decompressor):
  """XZ decompressor using lzma."""

  COMPRESSION_METHOD = definitions.COMPRESSION_METHOD_XZ

  def __init__(self):
    """Initializes a decompressor."""
    super(XZDecompressor, self).__init__()
    # Note that lzma.FORMAT_XZ does not work for every implementation of lzma.
    self._lzma_decompressor = lzma.LZMADecompressor(1)

  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data (bytes): compressed data.

    Returns:
      tuple(bytes, bytes): uncompressed data and remaining compressed data.

    Raises:
      BackEndError: if the XZ compressed stream cannot be decompressed.
    """
    try:
      if sys.version_info[0] < 3:
        # Note that we cannot use max_length=0 here due to different
        # versions of the lzma code.
        uncompressed_data = self._lzma_decompressor.decompress(
            compressed_data, 0)
      else:
        uncompressed_data = self._lzma_decompressor.decompress(compressed_data)

      remaining_compressed_data = getattr(
          self._lzma_decompressor, 'unused_data', b'')

    except (EOFError, IOError, LZMAError) as exception:
      raise errors.BackEndError((
          'Unable to decompress XZ compressed stream with error: '
          '{0!s}.').format(exception))

    return uncompressed_data, remaining_compressed_data


class LZMADecompressor(XZDecompressor):
  """LZMA decompressor using lzma."""

  COMPRESSION_METHOD = definitions.COMPRESSION_METHOD_LZMA

  def __init__(self):
    """Initializes a decompressor."""
    super(LZMADecompressor, self).__init__()
    # Note that lzma.FORMAT_ALONE does not work for every implementation
    # of lzma.
    self._lzma_decompressor = lzma.LZMADecompressor(2)


manager.CompressionManager.RegisterDecompressors([
    LZMADecompressor, XZDecompressor])
