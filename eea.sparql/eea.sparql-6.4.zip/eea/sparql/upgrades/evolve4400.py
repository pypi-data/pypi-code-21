""" Migrate sparqls with the new arguments format (name:type query)
"""

import logging
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from eea.sparql.async import IAsyncService
from eea.sparql.content.sparql import async_updateLastWorkingResults
import DateTime
import transaction

logger = logging.getLogger("eea.sparql.upgrades")


def restart_sparqls(context):
    """ Migrate sparqls with the new arguments format (name:type query)
    """

    async_service = queryUtility(IAsyncService)
    if async_service is None:
        logger.warn("Can't migrate_sparqls. plone.app.async NOT installed!")
        return

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type='Sparql')

    restarted = 0
    log_total = len(brains)
    log_count = 0
    restarted = 0
    for brain in brains:
        log_count += 1
        logger.info('PATH %s::%s: %s', log_count, log_total, brain.getPath())
        # added exceptions for broken spqrql methods
        if brain.getPath() != '/www/SITE/data-and-maps/daviz/sds/'\
            'show-eunis-and-dbpedia-links-1' and \
            brain.getPath() != '/www/SITE/sandbox/antonio-tests/aq' and \
            brain.getPath() != '/www/SITE/sandbox/antonio-tests/aq-1' and \
            brain.getPath() != '/www/SITE/data-and-maps/daviz/eionet/data/'\
                'inspire-monitoring-and-reporting-atbe-ref-years-2011-2012':
            obj = brain.getObject()
            if obj.getRefresh_rate() != 'Once':
                obj.scheduled_at = DateTime.DateTime()
                async_queue = async_service.getQueues()['']
                async_service.queueJobInQueue(
                    async_queue, ('sparql',),
                    async_updateLastWorkingResults,
                    obj,
                    scheduled_at=obj.scheduled_at,
                    bookmarks_folder_added=False
                )
                restarted += 1
                transaction.commit()

    message = 'Restarted %s Sparqls ...' % restarted
    logger.info(message)
    return message
