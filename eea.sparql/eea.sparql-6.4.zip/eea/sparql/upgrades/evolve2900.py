""" Migrate sparqls for async update of last working results
"""

import datetime
import logging
import pytz

import DateTime
from Products.CMFCore.utils import getToolByName
from eea.sparql.content.sparql import async_updateLastWorkingResults
from eea.sparql.async import IAsyncService
from zope.component import queryUtility

logger = logging.getLogger("eea.sparql.upgrades")


def migrate_sparqls(context):
    """ Migrate sparqls for async update of last working results
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type='Sparql')

    logger.info('Migrating %s Sparqls ...', len(brains))
    already_migrated = 0
    has_args = 0
    async_service = queryUtility(IAsyncService)
    if async_service is None:
        logger.warn("Can't migrate_sparqls. plone.app.async NOT installed!")
        return

    for brain in brains:
        obj = brain.getObject()
        if getattr(obj, 'arg_spec', ''):
            has_args += 1
            continue
        if hasattr(obj, 'scheduled_at'):
            already_migrated += 1
            continue
        obj.refresh_rate = 'Daily'
        if getattr(obj, 'sparql_static', False):
            obj.refresh_rate = 'Once'
        cached_result = getattr(obj, 'cached_result', {})
        rows = cached_result.get('result', {}).get('rows', [])

        obj.scheduled_at = DateTime.DateTime()
        async_queue = async_service.getQueues()['']
        if not rows:
            async_service.queueJobInQueue(
                async_queue, ('sparql',),
                async_updateLastWorkingResults,
                obj,
                scheduled_at=obj.scheduled_at,
                bookmarks_folder_added=False
            )
        else:
            if obj.refresh_rate != 'Once':
                before = datetime.datetime.now(pytz.UTC)
                delay = before + datetime.timedelta(days=1)
                async_service.queueJobInQueueWithDelay(
                    None, delay,
                    async_queue, ('sparql',),
                    async_updateLastWorkingResults,
                    obj,
                    scheduled_at=obj.scheduled_at,
                    bookmarks_folder_added=False
                )

    logger.info('Migrated %s Sparqls ...',
                len(brains) - already_migrated - has_args)
    logger.info('Sparqls with arguments: %s...', has_args)
    logger.info('Already Migrated %s Sparqls ...', already_migrated)
    return "Sparql Migration Done"
