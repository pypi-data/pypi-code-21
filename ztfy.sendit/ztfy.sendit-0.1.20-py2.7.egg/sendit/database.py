### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages
import transaction

# import Zope3 interfaces
from z3c.language.negotiator.interfaces import INegotiatorManager
from zope.authentication.interfaces import IAuthentication
from zope.catalog.interfaces import ICatalog
from zope.component.interfaces import IComponentRegistry, ISite
from zope.i18n.interfaces import INegotiator
from zope.intid.interfaces import IIntIds
from zope.processlifetime import IDatabaseOpenedWithRoot

# import local interfaces
from ztfy.base.interfaces import IPathElements, IBaseContentType
from ztfy.i18n.interfaces.content import II18nBaseContent
from ztfy.security.interfaces import ISecurityManager, ILocalRoleManager, ILocalRoleIndexer
from ztfy.sendit.packet.interfaces import IPacket
from ztfy.utils.interfaces import INewSiteManagerEvent
from ztfy.utils.timezone.interfaces import IServerTimezone

# import Zope3 packages
from z3c.language.negotiator.app import Negotiator
from zc.catalog.catalogindex import SetIndex, ValueIndex, DateTimeValueIndex
from zope.app.publication.zopepublication import ZopePublication
from zope.catalog.catalog import Catalog
from zope.component import adapter, queryUtility
from zope.intid import IntIds
from zope.location import locate
from zope.pluggableauth.authentication import PluggableAuthentication
from zope.pluggableauth.plugins.groupfolder import GroupFolder, GroupInformation
from zope.pluggableauth.plugins.principalfolder import PrincipalFolder
from zope.site import hooks

# import local packages
from ztfy.utils.catalog.index import TextIndexNG
from ztfy.utils.site import locateAndRegister
from ztfy.utils.timezone.utility import ServerTimezoneUtility


def updateDatabaseIfNeeded(context):
    """Check for missing utilities at application startup"""
    try:
        sm = context.getSiteManager()
    except:
        return
    default = sm['default']
    # Check for required IIntIds utility
    intids = queryUtility(IIntIds)
    if intids is None:
        intids = default.get('IntIds')
        if intids is None:
            intids = IntIds()
            locate(intids, default)
            IComponentRegistry(sm).registerUtility(intids, IIntIds, '')
            default['IntIds'] = intids
    # Check authentication utility
    auth = default.get('Authentication')
    if auth is None:
        auth = PluggableAuthentication()
        locateAndRegister(auth, default, 'Authentication', intids)
        auth.credentialsPlugins = [ u'No Challenge if Authenticated',
                                    u'Session Credentials',
                                    u'Zope Realm Basic-Auth' ]
        IComponentRegistry(sm).registerUtility(auth, IAuthentication)
    if 'users' not in auth:
        folder = PrincipalFolder('usr.')
        locateAndRegister(folder, auth, 'users', intids)
        auth.authenticatorPlugins += ('users',)
    groups = auth.get('groups', None)
    if groups is None:
        groups = GroupFolder('grp.')
        locateAndRegister(groups, auth, 'groups', intids)
        auth.authenticatorPlugins += ('groups',)
    roles_manager = ILocalRoleManager(context, None)
    if 'administrators' not in groups:
        group = GroupInformation('Administrators (group)', "Group of site administrators, which handle application configuration")
        locateAndRegister(group, groups, 'administrators', intids)
        if (roles_manager is None) or ('ztfy.SenditAdministrator' in roles_manager.__roles__):
            ISecurityManager(context).grantRole('ztfy.SenditAdministrator', 'grp.administrators', False)
    if 'managers' not in groups:
        group = GroupInformation('Managers (group)', "Group of site system services and utilities managers")
        locateAndRegister(group, groups, 'managers', intids)
        if (roles_manager is None) or ('ztfy.SenditManager' in roles_manager.__roles__):
            ISecurityManager(context).grantRole('ztfy.SenditManager', 'grp.managers', False)
    # Check server timezone
    tz = queryUtility(IServerTimezone)
    if tz is None:
        tz = default.get('Timezone')
        if tz is None:
            tz = ServerTimezoneUtility()
            locateAndRegister(tz, default, 'Timezone', intids)
            IComponentRegistry(sm).registerUtility(tz, IServerTimezone)
    # Check I18n negotiator
    i18n = queryUtility(INegotiatorManager)
    if i18n is None:
        i18n = default.get('I18n')
        if i18n is None:
            i18n = Negotiator()
            locateAndRegister(i18n, default, 'I18n', intids)
            i18n.serverLanguage = u'en'
            i18n.offeredLanguages = [u'en']
            IComponentRegistry(sm).registerUtility(i18n, INegotiator)
            IComponentRegistry(sm).registerUtility(i18n, INegotiatorManager)
    # Check for required catalog and index
    catalog = default.get('Catalog')
    if catalog is None:
        catalog = Catalog()
        locateAndRegister(catalog, default, 'Catalog', intids)
        IComponentRegistry(sm).registerUtility(catalog, ICatalog, 'Catalog')
    if catalog is not None:
        if 'paths' not in catalog:
            index = SetIndex('paths', IPathElements, False)
            locateAndRegister(index, catalog, 'paths', intids)
        if 'content_type' not in catalog:
            index = ValueIndex('content_type', IBaseContentType, False)
            locateAndRegister(index, catalog, 'content_type', intids)
        if 'expiration_date' not in catalog:
            index = DateTimeValueIndex('expiration_date', IPacket, False, resolution=1)
            locateAndRegister(index, catalog, 'expiration_date', intids)
        if 'title' not in catalog:
            index = TextIndexNG('title shortname description heading', II18nBaseContent, False,
                                languages=('fr en'),
                                storage='txng.storages.term_frequencies',
                                dedicated_storage=False,
                                use_stopwords=True,
                                use_normalizer=True,
                                ranking=True)
            locateAndRegister(index, catalog, 'title', intids)
    # Check for security catalog and indexes
    catalog = default.get('SecurityCatalog')
    if catalog is None:
        catalog = Catalog()
        locateAndRegister(catalog, default, 'SecurityCatalog', intids)
        IComponentRegistry(sm).registerUtility(catalog, ICatalog, 'SecurityCatalog')
    if catalog is not None:
        if 'ztfy.SenditRecipient' not in catalog:
            index = SetIndex('ztfy.SenditRecipient', ILocalRoleIndexer, False)
            locateAndRegister(index, catalog, 'ztfy.SenditRecipient', intids)


@adapter(IDatabaseOpenedWithRoot)
def handleOpenedDatabase(event):
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    for site in root_folder.values():
        if ISite(site, None) is not None:
            hooks.setSite(site)
            updateDatabaseIfNeeded(site)
            transaction.commit()


@adapter(INewSiteManagerEvent)
def handleNewSiteManager(event):
    updateDatabaseIfNeeded(event.object)
