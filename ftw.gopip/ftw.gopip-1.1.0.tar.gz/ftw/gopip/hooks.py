from Products.CMFCore.utils import getToolByName
import logging


INDEX_NAME = 'getObjPositionInParent'
LOG = logging.getLogger('ftw.gopip')


def installed(site):
    LOG.info('Replacing {!r} index with a FieldIndex.'.format(INDEX_NAME))
    catalog = getToolByName(site, 'portal_catalog')
    catalog.delIndex(INDEX_NAME)
    catalog.addIndex(INDEX_NAME, 'FieldIndex')
    LOG.info('Reindexing {!r}'.format(INDEX_NAME))
    catalog.manage_reindexIndex(ids=[INDEX_NAME])


def uninstalled(site):
    LOG.info('Replacing {!r} index back to plone standard.'.format(INDEX_NAME))
    catalog = getToolByName(site, 'portal_catalog')
    catalog.delIndex(INDEX_NAME)
    catalog.addIndex(INDEX_NAME, 'GopipIndex')
