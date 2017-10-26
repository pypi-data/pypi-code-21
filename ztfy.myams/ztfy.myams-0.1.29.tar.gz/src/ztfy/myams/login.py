#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from z3c.form.interfaces import HIDDEN_MODE, IErrorViewSnippet
from z3c.json.interfaces import IJSONWriter
from zope.authentication.interfaces import IAuthentication
from zope.component.interfaces import ISite
from zope.security.interfaces import IUnauthorized
from zope.session.interfaces import ISession

# import local interfaces
from ztfy.baseskin.interfaces import IDefaultView, IDialog
from ztfy.myams.interfaces import IModalFullPage

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import ajax
from zope.component import adapts, getUtility, getUtilitiesFor, getMultiAdapter, queryMultiAdapter
from zope.interface import implements, Interface, Invalid
from zope.publisher.browser import BrowserPage
from zope.schema import TextLine, Password
from zope.site import hooks
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.baseskin.viewlet import ContentProviderBase
from ztfy.myams.form import AddForm
from ztfy.myams.layer import MyAMSLayer
from ztfy.utils.traversing import getParent

from ztfy.myams import _


class ILoginFormFields(Interface):
    """Login form fields interface"""

    username = TextLine(title=_("login-field", "Login"),
                        description=_("Principal ID or email address"),
                        required=True)

    password = Password(title=_("password-field", "Password"),
                        required=True)

    came_from = TextLine(title=_("camefrom-field", "Login origin"),
                         required=False)


class ILoginFormButtons(Interface):
    """Login form buttons interface"""

    login = button.Button(name='login', title=_("Login"))


class LoginView(AddForm):
    """Login view"""

    implements(IModalFullPage)

    legend = _("Please enter valid credentials to login")
    dialog_class = 'modal-medium'
    warn_on_change = False

    fields = field.Fields(ILoginFormFields)
    buttons = button.Buttons(ILoginFormButtons)
    handler = '/@@ajax/handleLogin'
    principal = None

    def updateWidgets(self, prefix=None):
        super(LoginView, self).updateWidgets(prefix)
        self.widgets['came_from'].mode = HIDDEN_MODE
        origin = self.request.get('came_from') or self.request.get(self.prefix + self.widgets.prefix + 'came_from')
        if not origin:
            origin = self.request.getURL()
            stack = self.request.getTraversalStack()
            if stack:
                origin += '/' + '/'.join(stack[::-1])
        self.widgets['came_from'].value = origin

    def updateActions(self):
        super(AddForm, self).updateActions()
        if 'login' in self.actions:
            self.actions['login'].addClass('btn-primary')

    def extractData(self, setErrors=True):
        data, errors = super(LoginView, self).extractData(setErrors)
        if errors:
            self.logout()
            return data, errors
        self.request.form['login'] = data['username']
        self.request.form['password'] = data['password']
        context = getParent(self.context, ISite)
        while context is not None:
            old_site = hooks.getSite()
            try:
                hooks.setSite(context)
                for name, auth in getUtilitiesFor(IAuthentication):
                    try:
                        self.principal = auth.authenticate(self.request)
                        if self.principal is not None:
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
            errors += (view, )
            if setErrors:
                self.widgets.errors = errors
                self.logout()
        return data, errors

    @ajax.handler
    def handleLogin(self):
        writer = getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            return writer.write(self.getAjaxErrors())
        if self.principal is not None:
            if IUnauthorized.providedBy(self.context):
                context, _layer, _permission = self.context.args
                return writer.write({'status': 'redirect',
                                     'location': absoluteURL(context, self.request)})
            else:
                came_from = data.get('came_from')
                if came_from:
                    return writer.write({'status': 'redirect',
                                         'location': came_from})
                else:
                    target = queryMultiAdapter((self.context, self.request, Interface), IDefaultView)
                    return writer.write({'status': 'redirect',
                                         'location': '%s/%s' % (absoluteURL(self.context, self.request),
                                                                target.viewname if target is not None else '@@index.html')})
        else:
            return writer.write({'status': 'redirect',
                                 'location': '%s/@@login.html?came_from=%s' % (absoluteURL(self.context, self.request),
                                                                               data.get('came_from'))})

    def logout(self):
        try:
            sessionData = ISession(self.request)['zope.pluggableauth.browserplugins']
            sessionData['credentials'] = None
        except KeyError:
            pass
        self.principal = None


class LoginDialogView(LoginView):
    """Login dialog view"""

    implements(IDialog)


class LoginViewFormPrefix(ContentProviderBase):
    """Login view form prefix"""

    adapts(Interface, MyAMSLayer, LoginView)


class LoginViewFormSuffix(ContentProviderBase):
    """Login view form suffix"""

    adapts(Interface, MyAMSLayer, LoginView)


class LogoutView(BrowserPage):
    """Logout view"""

    def __call__(self):
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
        self.request.response.redirect('%s/%s' % (absoluteURL(self.context, self.request),
                                                  target.viewname if target is not None else '@@index.html'))
        return u''
