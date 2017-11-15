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
from xmlrpclib import Fault

# import Zope3 interfaces
from z3c.form.interfaces import IErrorViewSnippet
from z3c.json.interfaces import IJSONWriter

# import local interfaces
from ztfy.sendit.client.interfaces import ISenditClientInfo, ISenditClient
from ztfy.sendit.profile.interfaces import IUserRegistrationInfo

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import jsaction, ajax
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, queryUtility, getMultiAdapter
from zope.i18n import translate
from zope.interface import Interface, Invalid

# import local packages
from ztfy.skin.form import EditForm, DialogAddForm

from ztfy.sendit import _


class SenditClientEditForm(EditForm):
    """Sendit client utility edit form"""

    legend = _("Sendit client properties")

    fields = field.Fields(ISenditClientInfo)


class ISenditPrincipalRegistrationFormButtons(Interface):
    """Default dialog add form buttons"""

    register = jsaction.JSButton(title=_("Register user"))
    cancel = jsaction.JSButton(title=_("Cancel"))


class SenditPrincipalRegistrationForm(DialogAddForm):
    """Sendit principal registration form"""

    legend = _("Register new external user")
    help = _("""Use this form to register a new external user. This recipient will have to activate his account before downloading any packet.\n"""
             """WARNING: once registered, such users are not private to your profile but are shared with all application users!""")

    fields = field.Fields(IUserRegistrationInfo).select('email', 'firstname', 'lastname', 'company_name')

    buttons = button.Buttons(ISenditPrincipalRegistrationFormButtons)
    prefix = 'register_dialog.'

    @jsaction.handler(buttons['register'])
    def register_handler(self, event, selector):
        return '$.ZTFY.form.add(this.form);'

    @jsaction.handler(buttons['cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'

    @ajax.handler
    def ajaxCreate(self):
        writer = getUtility(IJSONWriter)
        self.updateWidgets()
        error = None
        errors = ()
        client = queryUtility(ISenditClient)
        if client is None:
            error = Invalid(_("Missing Sendit client utility"))
            view = getMultiAdapter((error, self.request, None, None, self, self.context),
                                   IErrorViewSnippet)
            view.update()
            errors += (view,)
        if not errors:
            data, errors = self.extractData()
            if not errors:
                try:
                    info = client.registerPrincipal(data.get('email'),
                                                    data.get('firstname'),
                                                    data.get('lastname'),
                                                    data.get('company_name'))
                    if info is None:
                        raise Invalid(_("An unknown error occurred. Can't register external user."))
                except Fault, f:
                    error = Invalid(f.faultString)
                except Exception, e:
                    error = Invalid(translate(_("Can't register external principal: %s"), context=self.request) % e.message)
                if error:
                    view = getMultiAdapter((error, self.request, None, None, self, self.context),
                                           IErrorViewSnippet)
                    view.update()
                    errors += (view,)
        if errors:
            self.widgets.errors = errors
            self.status = self.formErrorsMessage
            return writer.write(self.getAjaxErrors())
        else:
            return writer.write({ 'output': u"OK" })
