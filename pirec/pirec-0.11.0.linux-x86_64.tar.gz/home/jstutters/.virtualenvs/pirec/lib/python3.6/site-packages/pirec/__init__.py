"""pirec is a module for recording the activity of file processing pipelines.

.. moduleauthor:: Jon Stutters <j.stutters@ucl.ac.uk>
"""

from .processresult import pipeline, record, call
from .__version__ import __version__


__all__ = ('pipeline', 'record', 'call')
