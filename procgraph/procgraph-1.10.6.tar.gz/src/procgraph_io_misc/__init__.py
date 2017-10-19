''' Miscellaneous functions to be better organized. '''

procgraph_info = {
    'requires': [('json', ('simplejson',))] # TODO: add cjson?
}


from procgraph import import_magic
json = import_magic(__name__, 'json')


from . import json_misc
from . import to_file
from . import pickling
