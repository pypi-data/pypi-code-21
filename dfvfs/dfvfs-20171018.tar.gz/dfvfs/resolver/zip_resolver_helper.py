# -*- coding: utf-8 -*-
"""The ZIP path specification resolver helper implementation."""

from __future__ import unicode_literals

# This is necessary to prevent a circular import.
import dfvfs.file_io.zip_file_io
import dfvfs.vfs.zip_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class ZipResolverHelper(resolver_helper.ResolverHelper):
  """ZIP resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return dfvfs.file_io.zip_file_io.ZipFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return dfvfs.vfs.zip_file_system.ZipFileSystem(resolver_context)


resolver.Resolver.RegisterHelper(ZipResolverHelper())
