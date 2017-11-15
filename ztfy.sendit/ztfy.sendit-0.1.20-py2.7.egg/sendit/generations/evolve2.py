#
# Copyright (c) 2013 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard library
import logging
logger = logging.getLogger('onf.medialib')

# import interfaces
from hurry.query.interfaces import IQuery
from transaction.interfaces import ITransactionManager
from zope.catalog.interfaces import ICatalog
from zope.intid.interfaces import IIntIds
from ztfy.sendit.app.interfaces import ISenditApplication

# import packages
from hurry.query.query import And
from hurry.query.value import Eq
from zope.app.publication.zopepublication import ZopePublication
from zope.component import getUtility, queryUtility
from zope.site import hooks
from ztfy.utils.catalog import indexObject


def evolve(context):
    """Change text indexes splitter"""
    root_folder = context.connection.root().get(ZopePublication.root_name, None)
    for site in root_folder.values():
        if ISenditApplication(site, None) is not None:
            logger.info("Updating packets expiration date...")
            hooks.setSite(site)
            query = getUtility(IQuery)
            intids = getUtility(IIntIds)
            catalog = queryUtility(ICatalog, name=u'Catalog')
            if catalog is not None:
                params = [Eq(('Catalog', 'content_type'), 'IPacket')]
                for count, packet in enumerate(query.searchResults(And(*params))):
                    if packet.backup_time in (0, 1, 3):
                        packet.backup_time += 1
                    elif packet.backup_time == 2:
                        packet.backup_time = 4
                    indexObject(packet, catalog, 'expiration_date', intids=intids)
                    if not count % 100:
                        ITransactionManager(catalog).savepoint()
