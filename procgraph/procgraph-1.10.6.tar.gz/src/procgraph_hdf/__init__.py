''' 
    This is a set of blocks to read and write logs in HDF_ format.
    
    You need the pytables_ package to be installed.
    
    .. _pytables: http://pytables.org
     
    .. _HDF: http://en.wikipedia.org/wiki/Hierarchical_Data_Format

'''
from procgraph import import_succesful, import_magic

procgraph_info = {
    # List of python packages 
    'requires': ['tables', 'hdflog']
}

tables = import_magic(__name__, 'tables')
hdflogs = import_magic(__name__, 'hdflog')

if import_succesful(hdflogs):
    from .hdfwrite import *
    from .hdfread import *
    from .hdfread_many import *
else:
    from procgraph import logger
#     logger.warning('Could not import hdflogs')

from procgraph import pg_add_this_package_models
pg_add_this_package_models(__file__, __package__)
