""" Main product initializer
"""
import os
from eea.downloads.config import ENVPATH, ENVNAME
from eea.downloads.content.DirectoryView import registerDirectory

def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
    name = ENVNAME()
    if not name:
        raise AttributeError('Missing environment var EEADOWNLOADS_NAME')

    path = ENVPATH()
    if not path:
        raise AttributeError('Missing environment var EEADOWNLOADS_PATH')
    elif not os.path.exists(path):
        os.makedirs(path)
    registerDirectory(path)
