### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2013 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages
from persistent import Persistent
from xmlrpclib import Binary

# import Zope3 interfaces
from zope.pluggableauth.interfaces import ICredentialsPlugin

# import local interfaces
from ztfy.sendit.client.interfaces import ISenditClient, ISenditClientDocument, ISenditClientPacket

# import Zope3 packages
from zope.component import queryUtility
from zope.container.contained import Contained
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.file.property import FileProperty
from ztfy.utils.protocol.xmlrpc import getClient
from ztfy.utils.request import getRequest, queryRequest

from ztfy.sendit import _


class SenditClientDocument(object):
    """Sendit client document"""

    implements(ISenditClientDocument)

    title = FieldProperty(ISenditClientDocument['title'])
    filename = FieldProperty(ISenditClientDocument['filename'])
    data = FieldProperty(ISenditClientDocument['data'])


class SenditClientPacket(object):
    """Sendit client packet"""

    implements(ISenditClientPacket)

    title = FieldProperty(ISenditClientPacket['title'])
    description = FieldProperty(ISenditClientPacket['description'])
    recipients = FieldProperty(ISenditClientPacket['recipients'])
    notification_mode = FieldProperty(ISenditClientPacket['notification_mode'])
    backup_time = FieldProperty(ISenditClientPacket['backup_time'])
    documents = FieldProperty(ISenditClientPacket['documents'])


class SenditClientUtility(Persistent, Contained):
    """Sendit XML-RPC client utility"""

    implements(ISenditClient)

    server_url = FieldProperty(ISenditClient['server_url'])

    def _getCredentials(self, request=None):
        plugin = queryUtility(ICredentialsPlugin, 'Session Credentials')
        if plugin is not None:
            if request is None:
                request = getRequest()
            creds = plugin.extractCredentials(request)
            if creds is not None:
                return (creds['login'], creds['password'])
        return (None, None)

    def _getHeaders(self, request=None):
        if request is None:
            request = queryRequest()
        if request is None:
            headers = None
        else:
            headers = { 'Accept-Language': request.getHeader('Accept-Language') }
        return headers

    def searchPrincipals(self, query, names=None, request=None, credentials=()):
        """Search principals matching given query"""
        if not self.server_url:
            raise ValueError, _("Can't execute client methods without defined SendIt server URL")
        credentials = credentials or self._getCredentials(request)
        xmlrpc = getClient(self.server_url, credentials, allow_none=1, headers=self._getHeaders(request))
        return xmlrpc.searchPrincipals(query, names)

    def getPrincipalInfo(self, principal_id, request=None, credentials=None):
        """Get user profile info"""
        if not self.server_url:
            raise ValueError, _("Can't execute client methods without defined SendIt server URL")
        credentials = credentials or self._getCredentials(request)
        xmlrpc = getClient(self.server_url, credentials, allow_none=1, headers=self._getHeaders(request))
        return xmlrpc.getPrincipalInfo(principal_id)

    def canRegisterPrincipal(self, request=None, credentials=None):
        """Check if external principals can be registered"""
        if not self.server_url:
            return False
        credentials = credentials or self._getCredentials(request)
        xmlrpc = getClient(self.server_url, credentials, allow_none=1, headers=self._getHeaders(request))
        return xmlrpc.canRegisterPrincipal()

    def registerPrincipal(self, email, firstname, lastname, company_name=None, request=None, credentials=None):
        """Create a new profile with given attributes"""
        if not self.server_url:
            raise ValueError, _("Can't execute client methods without defined SendIt server URL")
        credentials = credentials or self._getCredentials(request)
        xmlrpc = getClient(self.server_url, credentials, allow_none=1, headers=self._getHeaders(request))
        return xmlrpc.registerPrincipal(email, firstname, lastname, company_name)

    def uploadPacket(self, packet, request=None, credentials=None):
        """Send a new packet with given properties"""
        if not self.server_url:
            raise ValueError, _("Can't execute client methods without defined SendIt server URL")
        if not ISenditClientPacket.providedBy(packet):
            raise ValueError, _("Send packet must implement ISenditClientPacket interface")
        credentials = credentials or self._getCredentials(request)
        xmlrpc = getClient(self.server_url, credentials, allow_none=1, headers=self._getHeaders(request))
        documents = [ { 'title': document.title,
                        'filename': document.filename,
                        'data': Binary(document.data) } for document in packet.documents ]
        return xmlrpc.uploadPacket(packet.title,
                                   packet.description,
                                   packet.recipients,
                                   packet.notification_mode,
                                   packet.backup_time,
                                   documents)
