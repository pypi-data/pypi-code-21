from cs.commenteditor import commenteditorMessageFactory as _
from plone.app.discussion.browser.validator import CaptchaValidator
from plone.app.discussion.interfaces import ICaptcha
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry
from plone.z3cform.fieldsets import extensible
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import form, field, button
from zope.component import queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from Products.CMFPlone.utils import safe_unicode
from types import StringType
from types import UnicodeType


def safe_encode(text):
    return safe_unicode(text).encode('utf-8')


class EditForm(extensible.ExtensibleForm, form.Form):
    # use context to get widget data
    ignoreContext = False
    id = None
    label = _(u"Edit this comment")
    fields = field.Fields(IComment).omit('portal_type',
                                         '__parent__',
                                         '__name__',
                                         'comment_id',
                                         'mime_type',
                                         'creation_date',
                                         'modification_date',
                                         'title',
                                         'in_reply_to',
                                         )

    @button.buttonAndHandler(_(u"edit_comment_button",
        default=u"Edit Comment"),
        name='comment')
    def handleComment(self, action):
        # Validation form
        data, errors = self.extractData()
        if errors:
            return

        # Validate Captcha
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        portal_membership = getToolByName(self.context, 'portal_membership')
        if settings.captcha != 'disabled' and \
            settings.anonymous_comments and \
                portal_membership.isAnonymousUser():

            if 'captcha' not in data:
                data['captcha'] = u""
            captcha = CaptchaValidator(self.context,
                                       self.request,
                                       None,
                                       ICaptcha['captcha'],
                                       None)
            captcha.validate(data['captcha'])

        for k, v in data.items():
            if type(v) in [UnicodeType, StringType]:
                setattr(self.context, k, safe_encode(v))
            else:
                setattr(self.context, k, v)
        notify(ObjectModifiedEvent(self.context))

        IStatusMessage(self.request).addStatusMessage(
            _(u'The message was edited successfuly'))
        self.request.response.redirect(self.context.absolute_url())

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.widgets['text'].rows = 10
