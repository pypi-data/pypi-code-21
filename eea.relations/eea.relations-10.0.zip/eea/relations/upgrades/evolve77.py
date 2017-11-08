""" Upgrades for eea.relations 7.7
"""

import logging
import transaction
from persistent.list import PersistentList
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger("eea.relations.upgrades")

def add_eea_refs(context):
    """
    Add the eea_refs attribute to objects
    if the object has related items, put them in eea_refs
    """
    ctool = getToolByName(context, 'portal_catalog')
    brains = ctool()
    total = len(brains)
    logger.info("Total of %s objects", total)
    count = 0
    commit_every = 100
    for brain in brains:
        count += 1
        if count%commit_every == 0:
            logger.info('INFO: Subtransaction committed (%s/%s)',
                        count, total)
            transaction.commit()
        try:
            obj = brain.getObject()
            should_add_eea_refs = True
            if hasattr(obj, "eea_refs"):
                should_add_eea_refs = False
            if obj.meta_type == 'Sparql':
                try:
                    if len(obj.cached_result['result']['rows']) > 100000:
                        logger.warn("'WARNING: Sparql has too many rows %s",
                            brain.getPath())
                        should_add_eea_refs = False
                except Exception:
                    logger.warn("'WARNING: Sparql with problems: %s",
                        brain.getPath())
            if should_add_eea_refs:
                try:
                    obj.eea_refs = PersistentList(obj.getRawRelatedItems())
                except Exception:
                    obj.eea_refs = PersistentList()
        except Exception:
            logger.warn("'WARNING: brain with problems: %s",
                        brain.getPath())
    logger.info("Done adding eea_refs on objects")
