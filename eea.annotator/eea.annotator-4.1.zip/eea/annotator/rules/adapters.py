""" Content rules adapters
"""
from zope.component import queryAdapter
from plone.stringinterp.adapters import BaseSubstitution
from Products.CMFCore.utils import getToolByName
from eea.annotator.config import EEAMessageFactory as _
from eea.annotator.interfaces import IAnnotatorStorage

class CommentSubstitution(BaseSubstitution):
    """ Inline comment string substitution
    """
    def __init__(self, context, **kwargs):
        super(CommentSubstitution, self).__init__(context, **kwargs)
        self._session = None

    @property
    def session(self):
        """ User session
        """
        if self._session is None:
            sdm = getattr(self.context, 'session_data_manager', None)
            self._session = sdm.getSessionData(create=False) if sdm else {}
        return self._session

    @property
    def comment(self):
        """ Get changed inline comment
        """
        return self.session.get('comment', {})

    @property
    def reply(self):
        """ Get changed reply
        """
        return self.session.get('reply', {})

    @property
    def title(self):
        """ Inline comment title
        """
        return self.comment.get('text', u'')

    @property
    def quote(self):
        """ Inline comment quote
        """
        return self.comment.get('quote', u'')

    @property
    def userId(self):
        """ Inline comment user id
        """
        return self.comment.get('user', {}).get('id', u'')

    @property
    def userName(self):
        """ Inline comment user name
        """
        return self.comment.get('user', {}).get('name', u'')

    @property
    def userEmail(self):
        """ Inline comment user email
        """
        return self.getUserEmail(self.userId)

    @property
    def replyTitle(self):
        """ Inline comment reply title
        """
        return self.reply.get('reply', u'')

    @property
    def replyUserId(self):
        """ Inline comment reply user id
        """
        return self.reply.get('user', {}).get('id', u'')

    @property
    def replyUserName(self):
        """ Inline comment reply user name
        """
        return self.reply.get('user', {}).get('name', u'')

    @property
    def replyUserEmail(self):
        """ Inline comment reply user email
        """
        return self.getUserEmail(self.replyUserId)

    @property
    def usersIds(self):
        """ Inline comment involved users. Including manual subscriptions
        """
        users = set()
        users.add(self.userId)

        for reply in self.comment.get('replies', []):
            user = reply.get('user', {}).get('id', '')
            if not user:
                continue
            users.add(user)

        storage = queryAdapter(self.context, IAnnotatorStorage)
        if not storage:
            return users

        subscribers = storage.subscribers
        for user, subscribed in subscribers.items():
            # User doesn't want emails
            if not subscribed:
                if user in users:
                    users.remove(user)
            else:
                users.add(user)

        return users

    @property
    def usersEmails(self):
        """ Inline comment involved users emails. Including manual subscriptions
        """
        emails = (self.getUserEmail(username) for username in self.usersIds)
        return ', '.join(email for email in emails if email)

    def getUserEmail(self, username):
        """ Get email by user name
        """
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getMemberById(username)
        if not member:
            return u''

        return member.getProperty('email', u'')

    def safe_call(self):
        """ Safe call
        """
        return getattr(self, self.attribute, u'')
#
# String substitution adapters
#
class Title(CommentSubstitution):
    """ Inline comment
    """
    category = _(u'Inline comments')
    description = _(u'Inline comment title')
    attribute = u'title'

class Quote(CommentSubstitution):
    """ Inline commented text
    """
    category = _(u'Inline comments')
    description = _(u'Inline commented text')
    attribute = u'quote'

class UserId(CommentSubstitution):
    """ Inline commented user
    """
    category = _(u'Inline comments')
    description = _(u'Inline comment user id')
    attribute = u'userId'

class UserName(CommentSubstitution):
    """ Inline commented user
    """
    category = _(u'Inline comments')
    description = _(u'Inline comment user fullname')
    attribute = u'userName'

class UserEmail(CommentSubstitution):
    """ Inline commented user email
    """
    category = _(u'Inline comments')
    description = _(u'Inline comment user email')
    attribute = u'userEmail'

class ReplyTitle(CommentSubstitution):
    """ Inline comment reply text
    """
    category = _(u'Inline comments')
    description = _(u'Inline comment reply')
    attribute = u'replyTitle'

class ReplyUserId(CommentSubstitution):
    """ Inline comment reply user name
    """
    category = _(u'Inline comments')
    description = _(u'Inline comment reply user id')
    attribute = u'replyUserId'

class ReplyUserName(CommentSubstitution):
    """ Inline comment reply user name
    """
    category = _(u'Inline comments')
    description = _(u'Inline comment reply user fullname')
    attribute = u'replyUserName'

class ReplyUserEmail(CommentSubstitution):
    """ Inline comment reply user email
    """
    category = _(u'Inline comments')
    description = _(u'Inline comment reply user email')
    attribute = u"replyUserEmail"

class UsersEmails(CommentSubstitution):
    """ Inline comment reply user email
    """
    category = _(u'Inline comments')
    description = _(u'Inline comment users emails. '
                    u'Including manual subscriptions.')
    attribute = u"usersEmails"
