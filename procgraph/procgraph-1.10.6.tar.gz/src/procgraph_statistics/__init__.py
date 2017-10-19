''' 
    Blocks for common statistical operations.

'''
from procgraph import import_magic


procgraph_info = {
    # List of python packages 
    'requires': ['astatsa', 'numpy']
}

np = import_magic(__name__, 'numpy')

from . import expectation
from . import variance
from . import covariance
from . import cov2corr
from . import minimum
from . import covariance2
