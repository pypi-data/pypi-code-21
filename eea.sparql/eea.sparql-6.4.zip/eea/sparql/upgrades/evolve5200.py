""" Migrate cached_result attribute for sparql objects
"""

import logging
from Products.CMFCore.utils import getToolByName
import transaction

logger = logging.getLogger("eea.sparql.upgrades")


def migrate_sparql_cached_result(context):
    """ Migrate Sparql's cached_result to a blob field
    """

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type='Sparql', Language='all',
                                   show_inactive=True)

    log_total = len(brains)
    log_count = 0
    migrated = 0
    for brain in brains:
        log_count += 1
        try:
            obj = brain.getObject()
        except Exception:
            logger.info('FAILED getObject %s:%s: %s', log_count, log_total,
                        brain.getPath())
            continue

        if getattr(obj, 'cached_result', None):
            logger.info('PATH %s:%s: %s', log_count, log_total, brain.getPath())
            obj.setSparqlCacheResults(obj.cached_result)
            obj.cached_result.clear()
            try:
                del obj.cached_result
            except AttributeError:
                # we can't delete the dict however we are ok with at least
                # emptying the results from it therefore we allow the
                # transaction to be made
                pass
            migrated += 1
            transaction.commit()
            if log_count % 100 == 0:
                logger.info('INFO: Transaction committed to zodb (%s/%s)',
                            log_count, log_total)

    message = 'Migrated cached_result for %s Sparqls ...' % migrated
    logger.info(message)
    return message


def add_sparql_max_row_length_properties(context):
    """ Add site properties sparql max rows length and msg
    """
    pprop = getToolByName(context, 'portal_properties')
    site_properties = pprop.site_properties
    if not site_properties.hasProperty('sparql_max_row_length'):
        site_properties._setProperty('sparql_max_row_length', 9000, 'int')
    if not site_properties.hasProperty('sparql_max_row_msg'):
        msg = "The SPARQL query returns a large results of %s rows." \
             " We recommend to limit the query in order to be below %s"
        site_properties._setProperty('sparql_max_row_msg', msg, 'text')
