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
import random
import string
from datetime import datetime
from os import urandom

# import Zope3 interfaces
from z3c.form.interfaces import IErrorViewSnippet, HIDDEN_MODE
from z3c.language.switch.interfaces import II18n
from zope.pluggableauth.interfaces import IAuthenticatorPlugin, IPrincipalInfo
from zope.publisher.interfaces import NotFound
from zope.sendmail.interfaces import IMailDelivery

# import local interfaces
from ztfy.appskin.interfaces import IAnonymousPage
from ztfy.mail.interfaces import IPrincipalMailInfo
from ztfy.security.interfaces import ISecurityManager
from ztfy.sendit.app.interfaces import FilterException
from ztfy.sendit.profile.interfaces import IProfile, IUserBaseRegistrationInfo, IUserRegistrationInfo, \
                                           IUserRegistrationConfirmInfo
from ztfy.sendit.user.interfaces import ISenditApplicationUsers

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import jsaction
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapts, queryUtility, getMultiAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements, Interface, Invalid
from zope.lifecycleevent import ObjectCreatedEvent
from zope.pluggableauth.plugins.principalfolder import InternalPrincipal
from zope.schema.fieldproperty import FieldProperty
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.mail.message import HTMLMessage
from ztfy.sendit.profile import getUserProfile
from ztfy.skin.form import BaseAddForm, BaseDialogAddForm
from ztfy.skin.page import TemplateBasedPage

from ztfy.sendit import _


#
# User registration
#

class PrincipalInfoRegistrationAdapter(object):
    """Principal info registration adapter"""

    adapts(IPrincipalInfo)
    implements(IUserBaseRegistrationInfo)

    email = FieldProperty(IUserRegistrationInfo['email'])
    firstname = FieldProperty(IUserRegistrationInfo['firstname'])
    lastname = FieldProperty(IUserRegistrationInfo['lastname'])
    company_name = FieldProperty(IUserRegistrationInfo['company_name'])
    password = FieldProperty(IUserRegistrationInfo['password'])
    confirm_password = FieldProperty(IUserRegistrationInfo['confirm_password'])

    def __init__(self, context):
        self.email = context.login
        self.lastname, self.firstname = context.title.split(' ', 1)
        self.company_name = context.description


class UserRegistrationForm(BaseAddForm):
    """User registration form"""

    implements(IAnonymousPage)

    legend = _("Please enter registration info")
    shortname = _("Registration")
    icon_class = 'icon-user'

    fields = field.Fields(IUserRegistrationInfo)
    registration_message_template = ViewPageTemplateFile('templates/register_message.pt')

    def __call__(self):
        if not self.context.open_registration:
            raise NotFound(self.context, 'register.html', self.request)
        return super(UserRegistrationForm, self).__call__()

    def updateActions(self):
        super(UserRegistrationForm, self).updateActions()
        self.actions['register'].addClass('btn btn-inverse')

    @button.buttonAndHandler(_('Register'), name='register')
    def handleRegister(self, action):
        data, errors = self.extractData()
        if not errors:
            error = None
            plugin = queryUtility(IAuthenticatorPlugin, self.context.external_auth_plugin)
            if plugin.has_key(data.get('email').lower()):
                error = Invalid(_("Address already used"))
            else:
                try:
                    self.context.checkAddressFilters(data.get('email').lower())
                except FilterException:
                    error = Invalid(_("This email domain or address has been excluded by system administrator"))
            if error:
                view = getMultiAdapter((error, self.request, self.widgets['email'],
                                        self.widgets['email'].field, self, self.context),
                                       IErrorViewSnippet)
                view.update()
                errors += (view,)
                self.widgets.errors = errors
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    def create(self, data):
        # create principal
        email = data.get('email').lower()
        principal = InternalPrincipal(login=email,
                                      password=data.get('password'),
                                      title='%s %s' % (data.get('lastname'), data.get('firstname')),
                                      description=data.get('company_name') or '')
        notify(ObjectCreatedEvent(principal))
        # create profile
        plugin = queryUtility(IAuthenticatorPlugin, self.context.external_auth_plugin)
        profile = getUserProfile(plugin.prefix + principal.login)
        profile.generateSecretKey(email, data.get('password'))
        # prepare notification message
        mailer = queryUtility(IMailDelivery, self.context.mailer_name)
        if mailer is not None:
            self.request.form['hash'] = profile.activation_hash
            message_body = self.registration_message_template(request=self.request,
                                                              context=self.context,
                                                              hash=profile.activation_hash)
            message = HTMLMessage(subject=translate(_("[%s] Please confirm registration"),
                                                    context=self.request) %
                                          II18n(self.context).queryAttribute('mail_subject_header',
                                                                             request=self.request),
                                  fromaddr="%s <%s>" % (self.context.mail_sender_name,
                                                        self.context.mail_sender_address),
                                  toaddr="%s <%s>" % (principal.title, principal.login),
                                  html=message_body)
            mailer.send(self.context.mail_sender_address, (principal.login,), message.as_string())
        return principal

    def add(self, object):
        plugin = removeSecurityProxy(queryUtility(IAuthenticatorPlugin, self.context.external_auth_plugin))
        plugin[object.login] = object
        ISecurityManager(object).grantRole('ztfy.SenditProfileOwner', plugin.prefix + object.login)
        ISecurityManager(object).grantRole('zope.Manager', plugin.prefix + object.login)

    def updateContent(self, object, data):
        pass

    def nextURL(self):
        return '%s/@@register_ok.html' % absoluteURL(self.context, self.request)


class UserRegistrationOK(TemplateBasedPage):
    """User registration confirm view"""

    implements(IAnonymousPage)

    def __call__(self):
        if not self.context.open_registration:
            raise NotFound(self.context, 'register_ok.html', self.request)
        return super(UserRegistrationOK, self).__call__()


#
# External user registration form
#

class IExternalUserRegistrationFormButtons(Interface):
    """Default dialog add form buttons"""

    register = jsaction.JSButton(title=_("Register user"))
    cancel = jsaction.JSButton(title=_("Cancel"))


def generatePassword(length=20):
    """Small password generator"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (urandom(1024))
    return ''.join(random.choice(chars) for _i in range(length))


class ExternalUserRegistrationForm(BaseDialogAddForm):
    """External user registration form
    
    This form is usable by internal users to declare external users.
    Form can always be used even when auto-registration is enabled.
    """

    legend = _("Register new external user")
    help = _("""Use this form to register a new external user. This recipient will have to activate his account before downloading any packet.\n"""
             """WARNING: once registered, such users are not private to your profile but are shared with all application users!""")
    icon_class = 'icon-user'

    fields = field.Fields(IUserRegistrationInfo).select('email', 'firstname', 'lastname', 'company_name')
    registration_message_template = ViewPageTemplateFile('templates/register_message.pt')

    buttons = button.Buttons(IExternalUserRegistrationFormButtons)
    prefix = 'register_dialog.'

    @jsaction.handler(buttons['register'])
    def register_handler(self, event, selector):
        return '$.ZTFY.form.add(this.form);'

    @jsaction.handler(buttons['cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'

    def updateActions(self):
        super(ExternalUserRegistrationForm, self).updateActions()
        self.actions['register'].addClass('btn btn-inverse')
        self.actions['cancel'].addClass('btn')

    def extractData(self, setErrors=True):
        data, errors = super(ExternalUserRegistrationForm, self).extractData(setErrors)
        if not errors:
            error = None
            plugin = queryUtility(IAuthenticatorPlugin, self.context.external_auth_plugin)
            email = data.get('email').lower()
            if plugin.has_key(email):
                error = Invalid(_("Address already used"))
            else:
                try:
                    self.context.checkAddressFilters(email)
                except FilterException:
                    error = Invalid(_("This email domain or address has been excluded by system administrator"))
            if error:
                view = getMultiAdapter((error, self.request, self.widgets['email'], self.widgets['email'].field, self, self.context),
                                       IErrorViewSnippet)
                view.update()
                errors += (view,)
                self.widgets.errors = errors
        if errors:
            self.status = self.formErrorsMessage
        return data, errors

    def create(self, data):
        # create principal
        email = data.get('email').lower()
        password = generatePassword()
        principal = InternalPrincipal(login=email,
                                      password=password,
                                      title='%s %s' % (data.get('lastname'), data.get('firstname')),
                                      description=data.get('company_name') or '')
        notify(ObjectCreatedEvent(principal))
        # create profile
        plugin = queryUtility(IAuthenticatorPlugin, self.context.external_auth_plugin)
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
                                          II18n(self.context).queryAttribute('mail_subject_header', request=self.request),
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
        return principal

    def add(self, object):
        plugin = removeSecurityProxy(queryUtility(IAuthenticatorPlugin, self.context.external_auth_plugin))
        plugin[object.login] = object
        ISecurityManager(object).grantRole('ztfy.SenditProfileOwner', plugin.prefix + object.login)
        ISecurityManager(object).grantRole('zope.Manager', plugin.prefix + object.login)

    def updateContent(self, object, data):
        pass


#
# Registration confirmation
#

class UserRegistrationConfirm(BaseAddForm):
    """User registration confirmation form"""

    implements(IAnonymousPage)

    legend = _("Registration confirmation form")
    shortname = _("Registration")
    icon_class = 'icon-user'

    fields = field.Fields(IUserRegistrationConfirmInfo)

    def updateWidgets(self):
        super(UserRegistrationConfirm, self).updateWidgets()
        self.widgets['activation_hash'].mode = HIDDEN_MODE
        self.widgets['activation_hash'].value = self.request.form.get('hash') or self.widgets['activation_hash'].value

    def updateActions(self):
        super(UserRegistrationConfirm, self).updateActions()
        self.actions['register'].addClass('btn btn-inverse')

    @button.buttonAndHandler(_('Confirm registration'), name='register')
    def handleRegister(self, action):
        data, errors = self.extractData()
        if not errors:
            email = data.get('email').lower()
            plugin = queryUtility(IAuthenticatorPlugin, self.context.external_auth_plugin)
            profile = getUserProfile(plugin.prefix + email, create=False)
            try:
                profile.checkActivation(data.get('activation_hash'), email, data.get('password'))
            except:
                error = Invalid(_("Can't validate activation. Please check your password and activation key."))
                view = getMultiAdapter((error, self.request, None, None, self, self.context),
                                       IErrorViewSnippet)
                view.update()
                errors += (view,)
                self.widgets.errors = errors
            else:
                profile.activation_date = datetime.utcnow()
                profile.activated = True
                ISenditApplicationUsers(self.context).addUserFolder(plugin.prefix + email)
        if errors:
            self.status = self.formErrorsMessage
            return
        self._finishedAdd = True

    def nextURL(self):
        return '%s/@@register_finish.html' % absoluteURL(self.context, self.request)


class UserRegistrationFinish(TemplateBasedPage):
    """User registration finished view"""

    implements(IAnonymousPage)
