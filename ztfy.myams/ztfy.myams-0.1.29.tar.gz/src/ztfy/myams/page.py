#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages
from datetime import datetime

# import Zope3 interfaces
from persistent.interfaces import IPersistent
from z3c.json.interfaces import IJSONWriter
from z3c.template.interfaces import ILayoutTemplate
from zope.authentication.interfaces import IAuthentication
from zope.pagetemplate.interfaces import IPageTemplate

# import local interfaces
from zope.security.interfaces import IUnauthorized
from ztfy.myams.interfaces import IInnerPage, IModalPage

# import Zope3 packages
from z3c.template.template import getPageTemplate, getLayoutTemplate
from zope.component import getMultiAdapter, getUtility
from zope.i18n import translate
from zope.interface import implements
from zope.publisher.browser import BrowserPage
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.utils.date import formatDatetime
from ztfy.utils.text import textToHTML
from ztfy.utils.timezone import tztime
from ztfy.utils.traversing import getParent

from ztfy.myams import _


class BaseTemplateBasedPage(BrowserPage):
    """Base template based page"""

    template = getPageTemplate()

    def __call__(self):
        self.update()
        return self.render()

    def update(self):
        pass

    def render(self):
        if self.template is None:
            template = getMultiAdapter((self, self.request), IPageTemplate)
            return template(self)
        return self.template()


class TemplateBasedPage(BaseTemplateBasedPage):
    """Template based page"""

    layout = getLayoutTemplate()

    def __call__(self):
        self.update()
        if self.layout is None:
            layout = getMultiAdapter((self, self.request), ILayoutTemplate)
            return layout(self)
        return self.layout()


class BaseIndexPage(TemplateBasedPage):
    """Base index page"""


class InnerPage(TemplateBasedPage):
    """Inner page"""

    implements(IInnerPage)


class ModalPage(TemplateBasedPage):
    """Modal page"""

    implements(IModalPage)


class ExceptionView(BrowserPage):
    """Base exception view"""

    @property
    def error_name(self):
        return self.context.__class__.__name__

    @property
    def error_message(self):
        return textToHTML(translate(getattr(self.context, 'message', u''), context=self.request) or
                          '\n'.join((str(arg) for arg in self.context.args)),
                          request=self.request)

    @property
    def error_datetime(self):
        return formatDatetime(tztime(datetime.utcnow()))

    @property
    def error_user(self):
        principal = self.request.principal
        return '%s (%s)' % (principal.title, principal.id)

    def __call__(self):
        self.request.response.setStatus(500)
        writer = getUtility(IJSONWriter)
        return writer.write({'status': 'messagebox',
                             'messagebox': {'status': 'error',
                                            'title': translate(_("An error occurred: %s"), context=self.request) %
                                                     self.error_name,
                                            'content': self.error_message,
                                            'number': self.error_datetime,
                                            'icon': 'fa fa-warning animated shake'}})


class UnauthorizedExceptionView(ExceptionView):
    """Unauthorized exception view"""

    def __call__(self):
        principal = self.request.principal
        auth = getUtility(IAuthentication)
        auth.unauthorized(principal.id, self.request)
        try:
            context = self.context.args[0]
        except:
            context = self.context
        self.request.response.setStatus(200)
        if ('/@@ajax/' in self.request.getURL()) or (self.request.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'):
            # Send JSON result when using AJAX
            parent = getParent(context, IPersistent)
            writer = getUtility(IJSONWriter)
            return writer.write({'status': 'modal',
                                 'location': 'login-dialog.html?came_from=%s' % absoluteURL(parent, self.request)})
        else:
            # else do a simple redirect...
            self.request.response.redirect('login.html?came_from=%s' % absoluteURL(context, self.request))
