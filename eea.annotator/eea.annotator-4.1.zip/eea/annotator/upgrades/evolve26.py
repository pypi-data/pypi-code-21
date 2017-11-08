""" Upgrade scripts to version 1.4
"""
import logging
from zope.component.hooks import getSite
from zope.component import queryAdapter
from persistent.dict import PersistentDict
from eea.annotator.interfaces import ISettings, IAnnotatorStorage
from Products.CMFCore.utils import getToolByName
logger = logging.getLogger('eea.annotator')

def fixBrokenComments(context):
    """ Fix comments without id and creation date
    """
    site = getSite()

    settings = queryAdapter(site, ISettings)
    ptypes = settings.portalTypes

    if not ptypes:
        logger.info('Nothing to fix')
        return 'Done'

    ctool = getToolByName(context, 'portal_catalog')
    brains = ctool.unrestrictedSearchResults(portal_type=ptypes)

    total = len(brains)
    logger.info('Searching to fix inline comments on %s objects of type %s',
                total, ptypes)

    for brain in brains:
        doc = brain.getObject()
        storage = queryAdapter(doc, IAnnotatorStorage)
        if not storage:
            continue

        comments = storage.comments
        if None not in comments:
            continue

        comment = storage._comments.pop(None)
        created = comment.get('created', comment.get('updated', storage.date))
        oid = storage.generateUniqueId(comment)
        comment['id'] = oid
        comment['created'] = created
        storage._comments[oid] = PersistentDict(comment)

        logger.info('Fixed broken inline comment for %s', doc.absolute_url())

    logger.info('Inline comments fix ... DONE')
    return 'Done fixing inline comments %s' % total
