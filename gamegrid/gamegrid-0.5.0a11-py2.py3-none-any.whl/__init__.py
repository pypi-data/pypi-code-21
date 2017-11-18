from ._version import version_info, __version__

from .gamegrid import *

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'gamegrid',
        'require': 'gamegrid/extension'
    }]
