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
import uuid
from random import randrange
from xmlrpclib import Binary

# import Zope3 interfaces
from z3c.language.switch.interfaces import II18n
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.sendmail.interfaces import IMailDelivery

# import local interfaces
from ztfy.mail.interfaces import IPrincipalMailInfo
from ztfy.security.interfaces import ISecurityManager
from ztfy.sendit.app.interfaces import FilterException
from ztfy.sendit.profile.interfaces import IProfile
from ztfy.sendit.skin.app.xmlrpc.interfaces import ISenditApplicationServices
from ztfy.sendit.user.interfaces import ISenditApplicationUsers

# import Zope3 packages
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtilitiesFor, queryUtility
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements
from zope.interface.exceptions import Invalid
from zope.lifecycleevent import ObjectCreatedEvent
from zope.pluggableauth.plugins.principalfolder import InternalPrincipal
from zope.publisher.xmlrpc import XMLRPCView
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.mail.message import HTMLMessage
from ztfy.security.search import findPrincipals, getPrincipal, MissingPrincipal
from ztfy.sendit.packet import Packet, Document
from ztfy.sendit.profile import getUserProfile
from ztfy.sendit.skin.app.registration import generatePassword
from ztfy.skin.form import FormObjectCreatedEvent

from ztfy.sendit import _


def getPrincipalTitle(principal):
    title = principal.title
    if '@' in principal.id:
        _name, domain = principal.id.split('@')
        title = '%s (%s)' % (title, domain)
    return title


class SenditApplicationServicePublisher(XMLRPCView):
    """Sendit application services publisher"""

    implements(ISenditApplicationServices)

    registration_message_template = ViewPageTemplateFile('../templates/register_message.pt')

    def searchPrincipals(self, query, names=None):
        """Search for registered principals"""
        app = self.context
        return [{'value': principal.id,
                 'caption': getPrincipalTitle(principal)}
                for principal in findPrincipals(query, names)
                if principal.id not in (app.excluded_principals or ())]

    def getPrincipalInfo(self, principal_id):
        """Get registered principal info, or None if not found"""
        for _name, plugin in getUtilitiesFor(IAuthenticatorPlugin):
            info = plugin.principalInfo(principal_id)
            if info is not None:
                return {'id': info.id,
                        'title': info.title}
        return None

    def canRegisterPrincipal(self):
        """Is external principals registration opened"""
        profile = IProfile(self.request.principal)
        name, _plugin, _info = profile.getAuthenticatorPlugin()
        if name is None:
            return False
        return name in self.context.internal_auth_plugins

    def registerPrincipal(self, email, firstname, lastname, company_name=None):
        """Create a new external principal"""
        # check for existing of filtered principal
        plugin = queryUtility(IAuthenticatorPlugin, self.context.external_auth_plugin)
        if plugin.has_key(email):
            raise Invalid(_("Address already used"))
        else:
            try:
                self.context.checkAddressFilters(email)
            except FilterException:
                raise Invalid(_("This email domain or address has been excluded by system administrator"))
        # create principal
        password = generatePassword()
        principal = InternalPrincipal(login=email,
                                      password=password,
                                      title='%s %s' % (lastname, firstname),
                                      description=company_name or u'')
        notify(ObjectCreatedEvent(principal))
        plugin[principal.login] = principal
        ISecurityManager(principal).grantRole('ztfy.SenditProfileOwner', plugin.prefix + principal.login)
        ISecurityManager(principal).grantRole('zope.Manager', plugin.prefix + principal.login)
        # create profile
        profile = getUserProfile(plugin.prefix + principal.login)
        profile.self_registered = False
        profile.generateSecretKey(email, password)
        # prepare notification message
        mailer = queryUtility(IMailDelivery, self.context.mailer_name)
        if mailer is not None:
            source_mail = None
            source_profile = IProfile(self.request.principal)
            source_info = IPrincipalMailInfo(source_profile, None)
            if source_info is None:
                _name, _plugin, principal_info = source_profile.getAuthenticatorPlugin()
                if principal_info is not None:
                    source_info = IPrincipalMailInfo(principal_info, None)
            if source_info is not None:
                source_mail = source_info.getAddresses()
                if source_mail:
                    source_mail = source_mail[0]
            if not source_mail:
                source_mail = (self.context.mail_sender_name, self.context.mail_sender_address)
            message_body = self.registration_message_template(request=self.request,
                                                              context=self.context,
                                                              hash=profile.activation_hash)
            message = HTMLMessage(subject=translate(_("[%s] Please confirm registration"), context=self.request) %
                                          II18n(self.context).queryAttribute('mail_subject_header',
                                                                             request=self.request),
                                  fromaddr="%s via %s <%s>" % (source_mail[0],
                                                               self.context.mail_sender_name,
                                                               self.context.mail_sender_address),
                                  toaddr="%s <%s>" % (principal.title, principal.login),
                                  html=message_body)
            message.add_header('Sender', "%s <%s>" % source_mail)
            message.add_header('Return-Path', "%s <%s>" % source_mail)
            message.add_header('Reply-To', "%s <%s>" % source_mail)
            message.add_header('Errors-To', source_mail[1])
            mailer.send(self.context.mail_sender_address, (principal.login,), message.as_string())
        info = plugin.principalInfo(plugin.prefix + principal.login)
        return info.id if info is not None else None

    def uploadPacket(self, title, description, recipients, notification_mode, backup_time, documents):
        """Create a new packet"""
        # Check profile quota
        profile = getUserProfile(self.request.principal)
        if profile.getQuotaUsage(self.context) >= (profile.getQuotaSize(self.context) * 1024 * 1024):
            raise ValueError, translate(_("Your storage quota is exceeded. You can't upload any new packet without "
                                          "freeing some space..."), context=self.request)
        # Check recipients
        errors = []
        if isinstance(recipients, (str, unicode)):
            recipients = recipients.split(',')
        for recipient in recipients:
            if isinstance(getPrincipal(recipient), MissingPrincipal):
                errors.append(recipient)
        if errors:
            raise ValueError, translate(_("Your packet contains unknown recipients: %s"), context=self.request) % \
                              ', '.join(errors)
        # Create new packet
        packet = Packet()
        notify(ObjectCreatedEvent(packet))
        packet.title = unicode(title, 'utf-8') if not isinstance(title, unicode) else title
        if description:
            packet.description = unicode(description, 'utf-8') if not isinstance(description, unicode) else description
        packet.recipients = recipients
        packet.notification_mode = notification_mode
        packet.backup_time = backup_time
        packet_name = str(uuid.uuid1(randrange(0, 1 << 48L) | 0x010000000000L))
        user = ISenditApplicationUsers(self.context).getUserFolder(self.request.principal)
        user[packet_name] = packet
        for doc_data in documents:
            if not isinstance(doc_data.get('data'), Binary):
                raise ValueError, translate(_("Document data must be set as XML-RPC binary"), context=self.request)
            document = Document()
            notify(ObjectCreatedEvent(document))
            document_name = str(uuid.uuid1(randrange(0, 1 << 48L) | 0x010000000000L))
            packet[document_name] = document
            title = doc_data.get('title') or translate(_("< document without title >"), context=self.request)
            document.title = unicode(title, 'utf-8') if not isinstance(title, unicode) else title
            document.data = doc_data.get('data').data
            filename = doc_data.get('filename')
            document.filename = unicode(filename, 'utf-8') if not isinstance(filename, unicode) else filename
        notify(FormObjectCreatedEvent(packet, self))
        return absoluteURL(packet, self.request)
