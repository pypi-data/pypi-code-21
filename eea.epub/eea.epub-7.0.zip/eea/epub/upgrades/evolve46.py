""" eea.epub 4.6 upgrade steps
"""
import logging
from types import InstanceType
from Products.CMFCore.utils import getToolByName
from eea.epub.mimetype import epub_mimetype

logger = logging.getLogger('eea.epub: setuphandlers')

def registerMimeType(self, mimetype):
    """ register mimetypes
    """
    if not isinstance(mimetype, InstanceType):
        mimetype = mimetype()
    mimetypes_registry = getToolByName(self, 'mimetypes_registry')
    mimetypes_registry.register(mimetype)
    logger.info("Registered mimetype %s", mimetype)

def installMimeTypes(self):
    """ Install epub mimetype
    """
    logger.info("Installing epub_mimetype mimetype")
    registerMimeType(self, epub_mimetype)
    logger.info("Done Installing epub_mimetype mimetype")

def reindexFileEpubs(self):
    """ Reindex epubs which were uploaded through file upload
    """
    catalog = getToolByName(self, 'portal_catalog')
    results = catalog.searchResults(filetype=('application/zip',
        'application/x-xcf', 'application/octet-stream',
        'application/xhtml+xml', 'text/css', 'text/html', 'text/xml'))
    for brain in results:
        if ".epub" in brain.id:
            obj = brain.getObject()
            obj.setFormat('application/epub+zip')
            obj.reindexObject()
            logger.info('obj migrated %s', obj.absolute_url(1))
