"""Common configuration constants
"""
import os
import logging
from zope.i18nmessageid import MessageFactory

logger = logging.getLogger('eea.downloads')

PROJECTNAME = 'eea.downloads'

def ENVPATH():
    """ GET EEADOWNLOADS_PATH from os env
    """
    path = os.environ.get('EEADOWNLOADS_PATH')
    if not path:
        path = os.environ.get('CLIENT_HOME', '/tmp')
        path = os.path.join(path, 'pdf')
        os.environ['EEADOWNLOADS_PATH'] = path
        logger.warn('Missing environment var EEADOWNLOADS_PATH. Using %s', path)
    return path

def ENVNAME():
    """ Get EEADOWNLOADS_NAME from os env
    """
    name = os.environ.get('EEADOWNLOADS_NAME')
    if not name:
        name = 'downloads'
        os.environ['EEADOWNLOADS_NAME'] = name
        logger.warn('Missing environment var EEADOWNLOADS_NAME. Using %s', name)
    return name

EEAMessageFactory = MessageFactory('eea')
