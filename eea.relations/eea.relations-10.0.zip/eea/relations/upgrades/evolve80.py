""" Upgrades for eea.relations 7.8
"""
import logging
import transaction
from persistent.list import PersistentList
from Products.CMFCore.utils import getToolByName
logger = logging.getLogger("eea.relations.upgrades")


def fix_eea_refs(context):
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
            should_fix_eea_refs = True
            if not hasattr(obj, "eea_refs"):
                should_fix_eea_refs = False
            if obj.meta_type == 'Sparql':
                try:
                    if len(obj.cached_result['result']['rows']) > 80000:
                        logger.warn("'WARNING: Sparql has too many rows %s",
                            brain.getPath())
                        should_fix_eea_refs = False
                except Exception:
                    logger.warn("'WARNING: Sparql with problems: %s",
                        brain.getPath())
            if should_fix_eea_refs:
                if not obj.eea_refs:
                    continue
                there_are_fixes = False
                fixed_refs = []
                for ref in obj.eea_refs:
                    if not isinstance(ref, basestring):
                        there_are_fixes = True
                        ref = ref.UID()
                    fixed_refs.append(ref)
                if there_are_fixes:
                    obj.eea_refs = PersistentList(fixed_refs)
                    logger.info('INFO: object fixed: %s', brain.getPath())
        except Exception, err:
            logger.warn("'WARNING: brain with problems: %s, %s",
                        brain.getPath(), err)
    logger.info("Done fixing eea_refs on objects")
