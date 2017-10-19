''' 
    An example package for ProcGraph that shows how to organize your code. 

    This is the documentation string for the package. Like all docstrings,
    it consists of a short summary (above) and a longer description (this.)
    
'''
import sys

# Specify all the meta-information in the 'procgraph_info' structure.
# You can omit all of this at first, then come back and fill it in once you 
# want your package to properly install on other people's machines.

procgraph_info = {
    # purely informational
    'author': 'Andrea Censi <andrea@cds.caltech.edu>',
    'project_url': 'http://procgraph.org',
    'scm': 'git@',

    # List of python packages 
    'requires': [
                  # try to add this
                  # 'unexistent',
                  ('pickle', ('cPickle', 'pickle')),
                  ],

    # List of external software needed
    'requires_executables': ['git'],

    # The following are more advanced, and used only for generating
    # rich cross-referenced documentation.
    'sphinx_base_url': 'http://andreacensi.github.com/procgraph/',
    'scm_base_url': 'https://github.com/AndreaCensi/procgraph/blob/master/',
}


from procgraph import import_magic

# If pickle is installed, it will be a reference to it, otherwise a 
# shadow object which will throw when you actually try to use it.
pickle = import_magic(__name__, 'pickle')

# procgraph will let you import unexistent modules
# unexistent = import_magic(__name__, 'unexistent')


# now, import the modules that defines the blocks
from . import example0_simplest_block

