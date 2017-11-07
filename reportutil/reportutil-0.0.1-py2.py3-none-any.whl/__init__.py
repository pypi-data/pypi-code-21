
import attr

# Get module version
from ._metadata import __version__

# Import key items from module
from .report import Report
from .constants import ReportConstant
from .components import ReportDir, HTMLReport


# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())


@attr.s
class _ReportTypes(object):
    root = attr.ib(default=Report, init=False)
    dir = attr.ib(default=ReportDir, init=False)
    file = attr.ib(default=HTMLReport, init=False)


ReportTypes = _ReportTypes()
