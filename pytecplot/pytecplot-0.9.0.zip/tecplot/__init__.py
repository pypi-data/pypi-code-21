# coding: utf-8
from __future__ import absolute_import, unicode_literals

"""`tecplot` is the top-level module for |PyTecplot| and it provides access
to the entire public API.

.. _hello_world:

In this example, the tecplot dynamic library is loaded at import time. The
|Tecplot Engine| is started and the text 'Hello, World!' is added to the
center of the active frame. All logging messages are piped to the console
which may be useful to debug any script::

    >>> import sys
    >>> import logging
    >>> import tecplot

    >>> logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    >>> frame = tecplot.active_frame()
    >>> frame.plot().text('Hello, World!', position=(35,50), height=35)
    >>> tecplot.export('hello_world.png')

TecUtil Layer
-------------

The interface used to access the |Tecplot Engine| is called "TecUtil" and is
the same as that used by addons. There are many checks in place for
validating calls into this layer. The vast majority of these are recoverable
and are seen in Python as a raised exception of type `TecplotLogicError`.

In principle, a user's script should never trigger a `TecplotLogicError` as
it indicates the requested operation is invalid in the current engine state
or that the parameters passed into the TecUtil layer (indexes for example)
are not valid. Here is a (contrived) example of a typical exception one might
see:

.. code-block:: python

    >>> import tecplot as tp
    >>> from tecplot.tecutil import lock
    >>> with tp.tecutil.lock():
    ...   tp.tecutil._tecutil.StateChangedX(None)
    Traceback (most recent call last):
      File "<stdin>", line 2, in <module>
      File "tecplot/tecutil/util.py", line 61, in _fn
        raise TecplotLogicError(errmsg)
    tecplot.exception.TecplotLogicError: Assertion trap in function call from
    an Add-on:

    Assertion Type: Pre-condition
    Assertion: ArgListIsValid(ArgList)
    Tecplot version: 16.3.0.72415
    Function: TecUtilStateChangedX
    Explanation: Argument list must be valid.

Note that `None` is an invalid input value for the ``StateChangedX()`` TecUtil
method.

Tecplot Version Compatibility
-----------------------------

It is always recommended to use the most recent version of |PyTecplot|. However,
doing so may require an update to the underlying |Tecplot 360| installation.
Out-of-date installations of |Tecplot 360| may be used but features may be
missing and care must be taken not to use such features in the Python scripts.
On top of this, there is a minimum version of the installed |Tecplot 360|
required by |PyTecplot| and the Python library will fail to load if this is
not satisfied.
"""

from . import (data, export, extension, layout, macro, constant, exception,
               session)
from .export.image import save_png, save_tiff, save_jpeg
from .layout import (active_frame, active_page, add_page, delete_page, frames,
                     load_layout, next_page, new_layout, page, pages,
                     save_layout)
from .session import stop, acquire_license, release_license
from .version import version as __version__
from .version import version_info, sdk_version, sdk_version_info

__author__ = 'Tecplot, Inc.'

__all__ = ['__version__', 'version_info', 'sdk_version', 'sdk_version_info',
           '__author__', 'data', 'export', 'extension', 'layout', 'macro',
           'constant', 'exception', 'session', 'active_frame', 'save_jpeg',
           'active_page', 'add_page', 'delete_page', 'load_layout', 'save_png',
           'new_layout', 'page', 'pages', 'save_layout', 'stop', 'save_tiff',
           'acquire_license', 'release_license']
