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

# import Zope3 interfaces
from z3c.language.switch.interfaces import II18n
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.sendmail.interfaces import IMailDelivery

# import local interfaces
from ztfy.mail.interfaces import IPrincipalMailInfo
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.sendit.app.interfaces.filter import IFilteringPlugin
from ztfy.sendit.packet.interfaces import IDocumentDownloadEvent, IPacket, IPacketDeleteEvent, \
                                          NOTIFICATION_NAMED, NOTIFICATION_NONE
from ztfy.sendit.profile.interfaces.history import IPacketHistory
from ztfy.sendit.user.interfaces import IUser
from ztfy.skin.interfaces import IFormObjectCreatedEvent

# import Zope3 packages
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter, queryUtility, getUtilitiesFor, getMultiAdapter
from zope.i18n import translate
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.traversing.api import getName

# import local packages
from ztfy.mail.message import HTMLMessage
from ztfy.sendit.profile import getUserProfile
from ztfy.sendit.profile.history import getUserProfileHistory
from ztfy.utils.list import unique
from ztfy.utils.traversing import getParent

from ztfy.sendit import _


#
# New packet notifications
#

RECIPIENT_NOTIFICATION_TEMPLATE = ViewPageTemplateFile('templates/recipient_notification.pt')

@adapter(IPacket, IFormObjectCreatedEvent)
def handleNewPacket(packet, event):
    """Send notification message to packet recipients"""
    app = getParent(packet, ISenditApplication)
    # get packet sender
    user = getParent(packet, IUser)
    source_profile = getUserProfile(user.owner)
    if source_profile.filtered_uploads:
        # execute filtering plug-ins
        for name in (app.filtering_plugins or ()):
            filter = queryUtility(IFilteringPlugin, name)
            if filter is not None:
                # this should raise an exception when an invalid packet is uploaded
                filter.filter(packet)
    # send mail notifications
    if not app.enable_notifications:
        return
    mailer = queryUtility(IMailDelivery, app.mailer_name)
    if mailer is None:
        return
    # get mail source
    source_mail = None
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
        source_mail = (app.mail_sender_name, app.mail_sender_address)
    # generate targets addresses
    recipients = packet.recipients.split(',')
    addresses = []
    for recipient in recipients:
        recipient_mail = None
        recipient_profile = getUserProfile(recipient, create=False)
        if recipient_profile is not None:
            recipient_mail = IPrincipalMailInfo(recipient_profile, None)
        if recipient_mail is None:
            for _name, plugin in getUtilitiesFor(IAuthenticatorPlugin):
                recipient_info = plugin.principalInfo(recipient)
                if recipient_info is not None:
                    recipient_mail = IPrincipalMailInfo(recipient_info, None)
                    if recipient_mail is not None:
                        break
        if recipient_mail is not None:
            addresses.extend(recipient_mail.getAddresses())
    # check for address uniqueness
    addresses = unique(addresses, idfun=lambda x: x[1])
    request = event.view.request
    for address in addresses:
        message_body = RECIPIENT_NOTIFICATION_TEMPLATE(event.view, app=app, packet=packet)
        message = HTMLMessage(subject=translate(_("[%s] A new packet is waiting for you"), context=request) % II18n(app).queryAttribute('mail_subject_header', request=request),
                              fromaddr="%s via %s <%s>" % (source_mail[0], app.mail_sender_name, app.mail_sender_address),
                              toaddr="%s <%s>" % address,
                              html=message_body)
        message.add_header('Sender', "%s <%s>" % source_mail)
        message.add_header('Return-Path', "%s <%s>" % source_mail)
        message.add_header('Reply-To', "%s <%s>" % source_mail)
        message.add_header('Errors-To', source_mail[1])
        mailer.send(app.mail_sender_address, (address[1],), message.as_string())


#
# Manual packet deletion notification
#

DELETE_NOTIFICATION_TEMPLATE = ViewPageTemplateFile('templates/delete_notification.pt')

@adapter(IPacketDeleteEvent)
def handleManuallyDeletedPacket(event):
    """Send notification message on package deletion"""
    packet = event.object
    app = getParent(packet, ISenditApplication)
    if not app.enable_notifications:
        return
    mailer = queryUtility(IMailDelivery, app.mailer_name)
    if mailer is None:
        return
    # get mail source
    user = getParent(packet, IUser)
    source_mail = None
    source_profile = getUserProfile(user.owner)
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
        source_mail = (app.mail_sender_name, app.mail_sender_address)
    # generate targets addresses
    recipients = packet.recipients.split(',')
    addresses = []
    for recipient in recipients:
        recipient_mail = None
        recipient_profile = getUserProfile(recipient, create=False)
        if recipient_profile is not None:
            recipient_mail = IPrincipalMailInfo(recipient_profile, None)
        if recipient_mail is None:
            for _name, plugin in getUtilitiesFor(IAuthenticatorPlugin):
                recipient_info = plugin.principalInfo(recipient)
                if recipient_info is not None:
                    recipient_mail = IPrincipalMailInfo(recipient_info, None)
                    if recipient_mail is not None:
                        break
        if recipient_mail is not None:
            addresses.extend(recipient_mail.getAddresses())
    # check for address uniqueness
    addresses = unique(addresses, idfun=lambda x: x[1])
    request = event.view.request
    for address in addresses:
        message_body = DELETE_NOTIFICATION_TEMPLATE(event.view, app=app, packet=packet)
        message = HTMLMessage(subject=translate(_("[%s] A packet has been deleted"), context=request) % II18n(app).queryAttribute('mail_subject_header', request=request),
                              fromaddr="%s via %s <%s>" % (source_mail[0], app.mail_sender_name, app.mail_sender_address),
                              toaddr="%s <%s>" % address,
                              html=message_body)
        message.add_header('Sender', "%s <%s>" % source_mail)
        message.add_header('Return-Path', "%s <%s>" % source_mail)
        message.add_header('Reply-To', "%s <%s>" % source_mail)
        message.add_header('Errors-To', source_mail[1])
        mailer.send(app.mail_sender_address, (address[1],), message.as_string())


#
# Handle all packet deletion to update owner's profile history
#

@adapter(IPacket, IObjectRemovedEvent)
def handleDeletedPacket(packet, event):
    """Update owner's history on packet deletion"""
    user = getParent(packet, IUser)
    history = getUserProfileHistory(user.owner)
    history[getName(packet)] = getMultiAdapter((packet, history), IPacketHistory)


#
# Download notification
#

DOWNLOAD_NOTIFICATION_TEMPLATE = ViewPageTemplateFile('templates/download_notification.pt')

@adapter(IDocumentDownloadEvent)
def handleDocumentDownload(event):
    """Send notification message on document download"""
    document = event.object
    app = getParent(document, ISenditApplication)
    if not app.enable_notifications:
        return
    mailer = queryUtility(IMailDelivery, app.mailer_name)
    if mailer is None:
        return
    request = event.request
    principal = event.downloader
    # check notification mode
    packet = getParent(document, IPacket)
    if (packet.notification_mode == NOTIFICATION_NONE) or \
       ((packet.notification_mode == NOTIFICATION_NAMED) and (principal.id not in packet.recipients.split(','))):
        return
    user = getParent(document, IUser)
    # get mail target
    target_mail = None
    target_profile = getUserProfile(user.owner)
    target_info = IPrincipalMailInfo(target_profile, None)
    if target_info is None:
        _name, _plugin, principal_info = target_profile.getAuthenticatorPlugin()
        if principal_info is not None:
            target_info = IPrincipalMailInfo(principal_info, None)
    if target_info is not None:
        target_mail = target_info.getAddresses()
        if target_mail:
            target_mail = target_mail[0]
    if not target_mail:
        return
    # get mail source
    source_mail = None
    source_profile = getUserProfile(principal.id)
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
        source_mail = (app.mail_sender_name, app.mail_sender_address)
    message_body = DOWNLOAD_NOTIFICATION_TEMPLATE(event.view, app=app, packet=packet, document=document, downloader=principal)
    message = HTMLMessage(subject=translate(_("[%s] Download notification"), context=request) % II18n(app).queryAttribute('mail_subject_header', request=request),
                          fromaddr="%s via %s <%s>" % (source_mail[0], app.mail_sender_name, app.mail_sender_address),
                          toaddr="%s <%s>" % target_mail,
                          html=message_body)
    message.add_header('Sender', "%s <%s>" % source_mail)
    message.add_header('Return-Path', "%s <%s>" % source_mail)
    message.add_header('Reply-To', "%s <%s>" % source_mail)
    message.add_header('Errors-To', source_mail[1])
    mailer.send(app.mail_sender_address, (target_mail[1],), message.as_string())
