### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#
##############################################################################


# import standard packages
from datetime import datetime
from httplib import UNAUTHORIZED

# import Zope3 interfaces
from z3c.form.interfaces import HIDDEN_MODE, IErrorViewSnippet
from z3c.language.switch.interfaces import II18n
from zope.authentication.interfaces import IAuthentication
from zope.component.interfaces import ISite
from zope.pluggableauth.interfaces import IAuthenticatedPrincipalCreated, IAuthenticatorPlugin
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.security.interfaces import IUnauthorized
from zope.sendmail.interfaces import IMailDelivery
from zope.session.interfaces import ISession

# import local interfaces
from ztfy.appskin.interfaces import IAnonymousPage
from ztfy.sendit.app.interfaces import ISenditApplication, EMAIL_REGEX, FilterException
from ztfy.sendit.profile.interfaces import IProfile
from ztfy.sendit.user.interfaces import ISenditApplicationUsers
from ztfy.skin.interfaces import IDefaultView

# import Zope3 packages
from z3c.form import field, button
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter, queryMultiAdapter, getMultiAdapter, queryUtility, getUtilitiesFor
from zope.i18n import translate
from zope.interface import implements, Interface, Invalid
from zope.publisher.skinnable import applySkin
from zope.schema import TextLine, Password
from zope.site import hooks
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.mail.message import HTMLMessage
from ztfy.sendit.profile import getUserProfile
from ztfy.skin.form import BaseAddForm
from ztfy.utils.traversing import getParent

from ztfy.sendit import _


class ILoginFormFields(Interface):
    """Login form fields interface"""

    username = TextLine(title=_("login-field", "Login"),
                        description=_("Principal ID or email address"),
                        required=True)

    password = Password(title=_("password-field", "Password"),
                        required=True)

    came_from = TextLine(title=_("camefrom-field", "Login origin"),
                         required=False)


def isUnauthorized(form):
    return IUnauthorized.providedBy(form.context)


def isUnauthorizedOrSubmitted(form):
    return isUnauthorized(form) or form.request.form.get(form.prefix + 'buttons.redirect')


def canRegister(form):
    if isUnauthorized(form):
        return False
    context = form.context
    app = getParent(context, ISenditApplication)
    return (app is not None) and app.open_registration


class LoginView(BaseAddForm):
    """Main login view"""

    implements(IAnonymousPage)

    legend = _("Please entel valid credentials to login")
    css_class = 'login_view'
    icon_class = 'icon-lock'
    disable_submit_flag = True

    fields = field.Fields(ILoginFormFields)

    def __call__(self):
        if isUnauthorized(self):
            context, _action, _permission = self.context.args
            self.request.response.setStatus(UNAUTHORIZED)
        else:
            context = self.context
        self.app = getParent(context, ISenditApplication)
        return super(LoginView, self).__call__()

    @property
    def action(self):
        return '%s/@@login.html' % absoluteURL(self.app, self.request)

    @property
    def help(self):
        profile = IProfile(self.request.principal, None)
        if (profile is not None) and profile.disabled:
            return _("This account is disabled. Please login with an enabled account or contact the administrator.")
        if canRegister(self):
            return _("Please enter login credentials or click 'Register' button to request a new account")

    def updateWidgets(self):
        super(LoginView, self).updateWidgets()
        self.widgets['came_from'].mode = HIDDEN_MODE
        origin = self.request.get('came_from') or self.request.get(self.prefix + self.widgets.prefix + 'came_from')
        if not origin:
            origin = self.request.getURL()
            stack = self.request.getTraversalStack()
            if stack:
                origin += '/' + '/'.join(stack[::-1])
        self.widgets['came_from'].value = origin

    def updateActions(self):
        super(LoginView, self).updateActions()
        self.actions['login'].addClass('btn')
        if canRegister(self):
            self.actions['register'].addClass('btn btn-warning')
        if isUnauthorized(self):
            self.actions['redirect'].addClass('btn btn-warning')
        self.actions['forgotten_password'].addClass('btn pull-right')

    def extractData(self, setErrors=True):
        data, errors = super(LoginView, self).extractData(setErrors=setErrors)
        if errors:
            self.logout()
            return data, errors
        self.request.form['login'] = data['username'].lower()
        self.request.form['password'] = data['password']
        self.principal = None
        context = getParent(self.context, ISite)
        while context is not None:
            old_site = hooks.getSite()
            try:
                hooks.setSite(context)
                for _name, auth in getUtilitiesFor(IAuthentication):
                    try:
                        self.principal = auth.authenticate(self.request)
                        if self.principal is not None:
                            profile = IProfile(self.principal)
                            if not profile.activated:
                                error = Invalid(_("This user profile is not activated. Please check your mailbox to get activation instructions."))
                                view = getMultiAdapter((error, self.request, None, None, self, self.context),
                                                       IErrorViewSnippet)
                                view.update()
                                errors += (view,)
                                if setErrors:
                                    self.widgets.errors = errors
                            return data, errors
                    except:
                        continue
            finally:
                hooks.setSite(old_site)
            context = getParent(context, ISite, allow_context=False)
        if self.principal is None:
            error = Invalid(_("Invalid credentials"))
            view = getMultiAdapter((error, self.request, None, None, self, self.context),
                                   IErrorViewSnippet)
            view.update()
            errors += (view,)
            if setErrors:
                self.widgets.errors = errors
            self.logout()
        return data, errors

    @button.buttonAndHandler(_("login-button", "Login"), name="login")
    def handleLogin(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        app = getParent(self.context, ISenditApplication)
        if self.principal is not None:
            ISenditApplicationUsers(app).addUserFolder(self.principal)
            if isUnauthorized(self):
                context, _action, _permission = self.context.args
                self.request.response.redirect(absoluteURL(context, self.request),
                                               trusted=app.trusted_redirects)
            else:
                came_from = data.get('came_from')
                if came_from:
                    self.request.response.redirect(came_from,
                                                   trusted=app.trusted_redirects)
                else:
                    target = queryMultiAdapter((self.context, self.request, Interface), IDefaultView)
                    self.request.response.redirect('%s/%s' % (absoluteURL(self.context, self.request),
                                                              target.viewname if target is not None else '@@index.html'),
                                                   trusted=app.trusted_redirects)
            return ''
        else:
            self.request.response.redirect('%s/@@login.html?came_from=%s' % (absoluteURL(self.context, self.request),
                                                                             data.get('came_from')),
                                           trusted=app.trusted_redirects)

    def logout(self):
        sessionData = ISession(self.request)['zope.pluggableauth.browserplugins']
        sessionData['credentials'] = None

    @button.buttonAndHandler(_("register-button", "Register"), name="register", condition=canRegister)
    def handleRegister(self, action):
        app = getParent(self.context, ISenditApplication)
        self.request.response.redirect('%s/@@register.html' % absoluteURL(self.context, self.request),
                                       trusted=app.trusted_redirects)

    @button.buttonAndHandler(_("home-button", "Go back home"), name="redirect", condition=isUnauthorizedOrSubmitted)
    def handleRedirect(self, action):
        app = getParent(self.context, ISenditApplication)
        self.request.response.redirect('%s/@@index.html' % absoluteURL(app, self.request),
                                       trusted=app.trusted_redirects)

    @button.buttonAndHandler(_("forgotten-password-button", "Forgotten password"), name="forgotten_password")
    def handleForgottenPassword(self, action):
        app = getParent(self.context, ISenditApplication)
        self.request.response.redirect('%s/@@forgotten_password.html' % absoluteURL(app, self.request),
                                       trusted=app.trusted_redirects)


class ForgottenPasswordView(BaseAddForm):
    """Forgotten password view"""

    implements(IAnonymousPage)

    legend = _("Please enter a valid e-mail address")
    css_class = 'login_view'
    icon_class = 'icon-lock'
    disable_submit_flag = True

    fields = field.Fields(ILoginFormFields).select('username')
    forgotten_password_template = ViewPageTemplateFile('templates/forgotten_password.pt')

    help = _("Please enter an already registered email address which will be used to send a new activation code.")

    def updateActions(self):
        super(ForgottenPasswordView, self).updateActions()
        self.actions['activate'].addClass('btn')

    def extractData(self, setErrors=True):
        data, errors = super(ForgottenPasswordView, self).extractData(setErrors)
        error = None
        if not EMAIL_REGEX.match(data['username']):
            error = Invalid(_("Given login is not a valid email address!"))
        else:
            try:
                self.context.checkAddressFilters(data['username'].lower())
            except FilterException:
                error = Invalid(_("This email domain or address has been excluded by system administrator"))
            else:
                plugin = queryUtility(IAuthenticatorPlugin, self.context.external_auth_plugin)
                if not plugin.has_key(data['username'].lower()):
                    error = Invalid(_("This email address is not registered!"))
        if error is not None:
            view = getMultiAdapter((error, self.request, None, None, self, self.context),
                                   IErrorViewSnippet)
            view.update()
            errors += (view,)
            if setErrors:
                self.widgets.errors = errors
        return data, errors

    @button.buttonAndHandler(_("activate", "Send activation code"), name='activate')
    def handleActivation(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        email = data.get('username').lower()
        # get profile
        plugin = queryUtility(IAuthenticatorPlugin, self.context.external_auth_plugin)
        profile = getUserProfile(plugin.prefix + email, create=False)
        if profile is not None:
            mailer = queryUtility(IMailDelivery, self.context.mailer_name)
            if mailer is not None:
                principal = plugin.get(email)
                message_body = self.forgotten_password_template(request=self.request,
                                                                context=self.context,
                                                                hash=profile.activation_hash)
                message = HTMLMessage(subject=translate(_("[%s] Forgotten password"),
                                                        context=self.request) %
                                              II18n(self.context).queryAttribute('mail_subject_header',
                                                                                 request=self.request),
                                      fromaddr="%s <%s>" % (self.context.mail_sender_name,
                                                        self.context.mail_sender_address),
                                      toaddr="%s <%s>" % (principal.title, principal.login),
                                      html=message_body)
                mailer.send(self.context.mail_sender_address, (principal.login,), message.as_string())
        self.request.response.redirect('%s/@@forgotten_password_ack.html' % absoluteURL(self.context, self.request),
                                       trusted=self.context.trusted_redirects)


class ForgottenPasswordAckView(BaseAddForm):
    """Forgotten password acknowledgement view"""

    implements(IAnonymousPage)

    legend = _("Activation message has been sent")
    css_class = 'login_view'
    icon_class = 'icon-lock'
    disable_submit_flah = True

    fields = field.Fields(Interface)
    buttons = button.Buttons(Interface)

    help = _("A new activation message has been sent to given email address. Please check your messages and follow "
             "the instructions.")


class LogoutView(BaseAddForm):
    """Main logout view"""

    def __call__(self):
        skin = queryUtility(IBrowserSkinType, self.context.getSkin())
        applySkin(self.request, skin)
        context = getParent(self.context, ISite)
        while context is not None:
            old_site = hooks.getSite()
            try:
                hooks.setSite(context)
                for _name, auth in getUtilitiesFor(IAuthentication):
                    auth.logout(self.request)
            finally:
                hooks.setSite(old_site)
            context = getParent(context, ISite, allow_context=False)
        target = queryMultiAdapter((self.context, self.request, Interface), IDefaultView)
        app = getParent(self.context, ISenditApplication)
        self.request.response.redirect('%s/%s' % (absoluteURL(self.context, self.request),
                                                  target.viewname if target is not None else '@@SelectedManagementView.html'),
                                       trusted=app.trusted_redirects)
        return ''


@adapter(IAuthenticatedPrincipalCreated)
def handleAuthenticatedPrincipal(event):
    """Handle authenticated principals
    
    Internal principals are automatically activated
    """
    app = getParent(event.authentication, ISenditApplication)
    if app is not None:
        profile = IProfile(event.principal)
        if not profile.activated:
            name, _plugin, _info = profile.getAuthenticatorPlugin()
            if name in app.internal_auth_plugins:
                profile.activation_date = datetime.utcnow()
                profile.activated = True
