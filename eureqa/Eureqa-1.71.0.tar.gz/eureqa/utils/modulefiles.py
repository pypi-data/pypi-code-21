# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import inspect
import os
from zipfile import ZipFile, is_zipfile
import types
import importlib

__all__ = [ 'module_path', 'open_module_file' ]

def module_path(module=None):
    if isinstance(module, basestring):
        module = importlib.import_module(module)

    if module is not None:
        module_filepath = module.__file__
    else:
        # Go find the module that our caller resides in.
        # The current module would not be useful.
        # Recurse in case we're called by another method in this file.
        frame = inspect.currentframe()
        base_module_filepath = inspect.getfile(frame)
        module_filepath = base_module_filepath
        while frame and module_filepath == base_module_filepath:
            frame = frame.f_back
            module_filepath = inspect.getfile(frame)

    return os.path.dirname(
        os.path.abspath(
            module_filepath))

def open_module_file(relative_filename, module=None):
    zip_file_path, path = _zipfile_path(
        os.path.join(module_path(module), relative_filename))
    if zip_file_path:
        zip_file = ZipFile(zip_file_path)
        # os.path.join will generate a path using '\\' as the separator on Windows but the path in the zipfile needs to use '/'
        zip_contained_file = zip_file.open(path.replace("\\","/"))

        # Monkey-patch in some logic to close the containing ZipFile when
        # we're done, so we don't leak file handles.
        # Icky but effective.
        existing_close = zip_contained_file.close
        def new_close(self):
            existing_close()
            zip_file.close()
        zip_contained_file.close = types.MethodType(new_close, zip_contained_file)

        return zip_contained_file
    else:
        return open(path)

def _zipfile_path(path):
    """ Given a path that may reside inside a zipfile,
    return a tuple of either (path, '') or
    (path to containing zipfile, path within zipfile)
    as strings."""
    ## Walk the provided path from leaf to root
    if not path or not isinstance(path, basestring):
        # What did you give us?
        # Also a base case for "os.path.split()", though we should
        # never get here since the previous base case should be
        # "/", which should match a subsequent clause.
        raise IOError, "Invalid argument.  Please provide a valid filesystem path."
    elif is_zipfile(path):
        # If we found a zipfile in our path, then we are in it.
        return (path, '')
    elif os.path.exists(path):
        # If we hit a valid POSIX path
        # before we hit a zipfile,
        # then the rest of the hierarchy must be all directories.
        # No zipfile here.  Short-circuit.
        return ('', path)
    else:
        # We're probably walking up a directory tree inside a zipfile.
        # It's expensive to validate this, so don't do so here.
        # Recurse.
        dirname, basename = os.path.split(path)
        zipfile, partial_path = _zipfile_path(dirname)
        return (zipfile, os.path.join(partial_path, basename))
