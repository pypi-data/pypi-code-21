''' 
    Blocks using Matplotlib to display data. 

'''

procgraph_info = {
    'requires': ['matplotlib', 'matplotlib.pylab']
}

# Smart dependencies initialization
from procgraph import import_magic, import_succesful
matplotlib = import_magic(__name__, 'matplotlib')
if import_succesful(matplotlib):
    if matplotlib.get_backend() != 'agg':
        matplotlib.use('agg')

pylab = import_magic(__name__, 'matplotlib.pylab')

from .pylab_to_image import pylab2rgb
from .plot_anim import PlotAnim
from .plot import *
from .plot_generic import *

# TODO: plot should fail for no inputs

from procgraph import pg_add_this_package_models
pg_add_this_package_models(__file__, __package__)
