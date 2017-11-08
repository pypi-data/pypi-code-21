""" Upgrades for eea.relations 4.6
"""
import logging
from Products.CMFCore.utils import getToolByName
logger = logging.getLogger("eea.relations.upgrades")

def reindexObjectProvides(context):
    """
    Reindex object_provides zCatalog index to add
    eea.relations.content.interfaces.IBaseObject interface to all
    BaseObject brains
    """
    logger.info('Reindexing object_provides...')
    ctool = getToolByName(context, 'portal_catalog')
    ctool.reindexIndex('object_provides', REQUEST=None)
    logger.info('Reindexing object_provides... DONE')
