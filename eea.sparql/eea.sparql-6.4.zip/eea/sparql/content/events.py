""" Handle events
"""
import logging
import DateTime
from zope.component import queryUtility
from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.statusmessages.interfaces import IStatusMessage
from eea.sparql.content.sparql import async_updateLastWorkingResults
from eea.sparql.interfaces import ISparqlBookmarksFolder
from eea.sparql.async import IAsyncService
logger = logging.getLogger("eea.sparql")


def bookmarksfolder_added(obj, evt):
    """On new bookmark folder automatically fetch all queries"""
    obj.syncQueries()


def sparql_added_or_modified(obj, evt):
    """Update last working results when sparql is added or modified"""
    async_service = queryUtility(IAsyncService)
    if async_service is None:
        logger.warn(
            "Can't schedule sparql update. plone.app.async NOT installed!")
        return

    obj.scheduled_at = DateTime.DateTime()

    bookmarks_folder_added = False
    if ISparqlBookmarksFolder.providedBy(obj) and \
        IObjectInitializedEvent.providedBy(evt):
        bookmarks_folder_added = True

    async_queue = async_service.getQueues()['']
    async_service.queueJobInQueue(
        async_queue, ('sparql',),
        async_updateLastWorkingResults,
        obj,
        scheduled_at=obj.scheduled_at,
        bookmarks_folder_added=bookmarks_folder_added)


def sparql_modified(obj, evt):
    """ Flush cache when the object is modified and show a portal message
    """
    obj.invalidateSparqlCacheResults()

    anchor_url = '%s/@@view#sparql-stats' % obj.absolute_url()

    IStatusMessage(obj.REQUEST).addStatusMessage(
        'The data will be updated shortly, please check \
        <a href="%s">the info</a> below.' % anchor_url,
        type='info')
