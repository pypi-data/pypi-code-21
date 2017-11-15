### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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
from persistent import Persistent
import re

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations
from zope.security.interfaces import IPrincipal

# import local interfaces
from ztfy.sendit.app.interfaces import ISenditApplication, ISenditApplicationBackInfo, FilterException
from ztfy.sendit.app.interfaces.filter import IFilteringPlugin

# import Zope3 packages
from zope.app.content import queryContentType
from zope.component import adapter, queryUtility, getUtility
from zope.event import notify
from zope.interface import implementer, implements, alsoProvides, noLongerProvides
from zope.location.location import locate, Location
from zope.schema.fieldproperty import FieldProperty
from zope.site.site import SiteManagerContainer

# import local packages
from ztfy.extfile.blob import BlobImage, BlobFile
from ztfy.file.property import FileProperty, ImageProperty
from ztfy.i18n.property import I18nTextProperty, I18nImageProperty
from ztfy.security.property import RolePrincipalsProperty
from ztfy.utils.site import NewSiteManagerEvent

from ztfy.sendit import _


class SenditApplication(Persistent, SiteManagerContainer):
    """Sendit application main class"""

    implements(ISenditApplication)

    __roles__ = ('ztfy.SenditManager', 'ztfy.SenditAdministrator')

    title = I18nTextProperty(ISenditApplication['title'])
    shortname = I18nTextProperty(ISenditApplication['shortname'])
    description = I18nTextProperty(ISenditApplication['description'])
    keywords = I18nTextProperty(ISenditApplication['keywords'])
    heading = I18nTextProperty(ISenditApplication['heading'])
    header = I18nImageProperty(ISenditApplication['header'], klass=BlobImage, img_klass=BlobImage)
    illustration = I18nImageProperty(ISenditApplication['illustration'], klass=BlobImage, img_klass=BlobImage)
    illustration_title = I18nTextProperty(ISenditApplication['illustration_title'])

    administrators = RolePrincipalsProperty(ISenditApplication['administrators'], role='ztfy.SenditAdministrator')
    managers = RolePrincipalsProperty(ISenditApplication['managers'], role='ztfy.SenditManager')

    open_registration = FieldProperty(ISenditApplication['open_registration'])
    confirmation_delay = FieldProperty(ISenditApplication['confirmation_delay'])
    internal_auth_plugins = FieldProperty(ISenditApplication['internal_auth_plugins'])
    external_auth_plugin = FieldProperty(ISenditApplication['external_auth_plugin'])
    single_auth_plugins = FieldProperty(ISenditApplication['single_auth_plugins'])
    _filtering_plugins = FieldProperty(ISenditApplication['filtering_plugins'])
    trusted_redirects = FieldProperty(ISenditApplication['trusted_redirects'])

    enable_notifications = FieldProperty(ISenditApplication['enable_notifications'])
    mailer_name = FieldProperty(ISenditApplication['mailer_name'])
    mail_service_owner = I18nTextProperty(ISenditApplication['mail_service_owner'])
    mail_service_name = I18nTextProperty(ISenditApplication['mail_service_name'])
    mail_sender_name = FieldProperty(ISenditApplication['mail_sender_name'])
    mail_sender_address = FieldProperty(ISenditApplication['mail_sender_address'])
    mail_subject_header = I18nTextProperty(ISenditApplication['mail_subject_header'])
    mail_signature = I18nTextProperty(ISenditApplication['mail_signature'])

    default_quota_size = FieldProperty(ISenditApplication['default_quota_size'])
    default_max_documents = FieldProperty(ISenditApplication['default_max_documents'])

    excluded_domains = FieldProperty(ISenditApplication['excluded_domains'])
    excluded_addresses = FieldProperty(ISenditApplication['excluded_addresses'])
    excluded_principals = FieldProperty(ISenditApplication['excluded_principals'])

    back_interface = ISenditApplicationBackInfo

    # Generic methods
    @property
    def content_type(self):
        return queryContentType(self).__name__

    def setSiteManager(self, sm):
        SiteManagerContainer.setSiteManager(self, sm)
        notify(NewSiteManagerEvent(self))

    # Skin management
    skin = 'Sendit'

    def getSkin(self):
        return self.skin

    # Filters management
    def checkAddressFilters(self, address):
        _name, domain = address.split('@')
        if domain in (self.excluded_domains or ()):
            raise FilterException, _("Given address is matching an excluded domain")
        for pattern in (self.excluded_addresses or ()):
            if re.match(pattern, address):
                raise FilterException, _("Given address is matching an exclusion filter")

    def checkPrincipalsFilters(self, principal):
        if IPrincipal.providedBy(principal):
            principal = principal.id
        if principal in self.excluded_principals.split(','):
            raise FilterException, _("Given principal is matching an exclusion filter")

    @property
    def filtering_plugins(self):
        return self._filtering_plugins

    @filtering_plugins.setter
    def filtering_plugins(self, value):
        old = set(self._filtering_plugins or ())
        new = set(value or ())
        removed = old - new
        added = new - old
        for name in removed:
            plugin = queryUtility(IFilteringPlugin, name=name)
            if plugin is not None:
                noLongerProvides(self, plugin.marker_interface)
        for name in added:
            plugin = getUtility(IFilteringPlugin, name=name)
            alsoProvides(self, plugin.marker_interface)
        self._filtering_plugins = value


class SenditApplicationBackInfo(Persistent, Location):
    """Medias library back-office presentation settings"""

    implements(ISenditApplicationBackInfo)

    custom_css = FileProperty(ISenditApplicationBackInfo['custom_css'], klass=BlobFile)
    custom_banner = ImageProperty(ISenditApplicationBackInfo['custom_banner'], klass=BlobImage, img_klass=BlobImage)
    custom_logo = ImageProperty(ISenditApplicationBackInfo['custom_logo'], klass=BlobImage, img_klass=BlobImage)
    custom_icon = ImageProperty(ISenditApplicationBackInfo['custom_icon'])


SENDIT_APPLICATION_BACK_INFO_KEY = 'ztfy.sendit.backoffice.presentation'

@adapter(ISenditApplication)
@implementer(ISenditApplicationBackInfo)
def SenditApplicationBackInfoFactory(context):
    annotations = IAnnotations(context)
    info = annotations.get(SENDIT_APPLICATION_BACK_INFO_KEY)
    if info is None:
        info = annotations[SENDIT_APPLICATION_BACK_INFO_KEY] = SenditApplicationBackInfo()
        locate(info, context, '++back++')
    return info
