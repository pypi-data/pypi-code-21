''' Various operations wrapping numpy functions. '''



procgraph_info = {
    # List of python packages
    'requires': ['numpy'],
}

from . import filters
from . import gradient1d
from . import smooth1d
