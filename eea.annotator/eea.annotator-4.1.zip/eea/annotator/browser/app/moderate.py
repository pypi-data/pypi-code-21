""" Moderate inline comments
"""
import hashlib
from copy import deepcopy
from datetime import datetime
from zope.event import notify
from zope.component import queryAdapter
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from eea.annotator.cache import cacheJsonKey, InvalidateCacheEvent
from eea.annotator.interfaces import  IAnnotatorStorage
from eea.annotator.config import EEAMessageFactory as _

class CommentView(BrowserView):
    """ Common
    """

    @property
    def cacheKey(self):
        """ Compute cache key
        """
        key = u"eea.annotator.browser.app.view.index:"
        key += cacheJsonKey(None, self)
        key = key.replace(
            u':%s' %  self.__name__,
            '/annotator.api:annotations_view')

        return hashlib.md5(key).hexdigest()


class Comments(CommentView):
    """ Moderate inline comments controller
    """
    @property
    def storage(self):
        """ Get storage adapter
        """
        return queryAdapter(self.context, IAnnotatorStorage)

    @property
    def comments(self):
        """ All comments sorted by date
        """
        def compare(a, b):
            """ Custom sorting cmp
            """
            a_up = datetime.strptime(a.get('updated'), "%Y-%m-%dT%H:%M:%S.%f")
            b_up = datetime.strptime(b.get('updated'), "%Y-%m-%dT%H:%M:%S.%f")
            return cmp(b_up, a_up)

        comments = deepcopy(self.storage.comments.values())

        # First we yield the length of this generator
        if comments:
            yield len(comments)
        else:
            yield 0

        # items
        for comment in sorted(comments, cmp=compare):
            created = comment['created']
            try:
                created = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%f")
            except Exception:
                created = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ")
            comment['created'] = created.strftime('%Y-%m-%d %H:%M')
            yield comment

    def redirect(self, to='', msg=''):
        """ redirect
        """
        if not to:
            to = u'%s/%s' % (
                self.context.absolute_url(),
                self.__name__
            )

        if msg:
            IStatusMessage(self.request).addStatusMessage(msg)
        return self.request.response.redirect(to)

    def close(self):
        """ Close comments
        """
        cids = self.request.get('comments', [])
        for cid in cids:
            comment = self.storage.get(cid)
            if not comment:
                continue
            comment['deleted'] = True
            self.storage.edit(comment)

        notify(InvalidateCacheEvent(key=self.cacheKey, raw=True))
        return self.redirect(msg=_('Comments closed'))

    def delete(self):
        """ Close comments
        """
        cids = self.request.get('comments', [])
        for cid in cids:
            comment = self.storage.get(cid)
            comment.pop('deleted', None)
            if not comment:
                continue
            self.storage.delete(comment)

        notify(InvalidateCacheEvent(key=self.cacheKey, raw=True))
        return self.redirect(msg=_('Comments deleted'))

    def __call__(self, *args, **kwargs):
        method = self.request.method
        if method.lower() != 'post':
            return self.index()

        close = self.request.form.pop('form.button.close', False)
        if close:
            return self.close()

        save = self.request.form.pop('form.button.delete', False)
        if save:
            return self.delete()

        self.redirect()


class Comment(CommentView):
    """ Moderate one comment
    """
    def __init__(self, context, request):
        super(Comment, self).__init__(context, request)
        self._comment = None

    @property
    def storage(self):
        """ Get storage adapter
        """
        return queryAdapter(self.context, IAnnotatorStorage)

    @property
    def comment(self):
        """ Comment
        """
        if self._comment is None:
            cid = self.request.get('id', None)
            self._comment = self.storage.comments.get(cid, {})
        return self._comment

    @property
    def replies(self):
        """ Comment replies
        """
        replies = deepcopy(self.comment.get('replies', []))

        # First we yield the length of this generator
        if replies:
            yield len(replies)
        else:
            yield 0

        for reply in replies:
            created = reply['created']
            try:
                created = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ")
            except Exception:
                created = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%f")
            reply['created'] = created.strftime('%Y-%m-%d %H:%M')
            yield reply

    def redirect(self, to='', msg=''):
        """ redirect
        """
        if not to:
            to = u'%s/%s?id=%s' % (
                self.context.absolute_url(),
                self.__name__,
                self.comment.get('id')
            )

        if msg:
            IStatusMessage(self.request).addStatusMessage(msg)
        return self.request.response.redirect(to)

    def save(self):
        """ Save comment
        """
        cid = self.request.get('id')
        text = self.request.get('text')
        username = self.request.get('user')
        del_replies = self.request.get('replies', [])

        comment = self.storage.get(cid)

        # Edit text
        if text:
            comment['text'] = text

        # Edit user
        if username:
            mtool = getToolByName(self.context, 'portal_membership')
            user = mtool.getMemberById(username)
            if user:
                comment['user'] = {
                    'id': username,
                    'name': user.getProperty('fullname')
                }

        # Delete replies
        for reply in comment.get('replies', []):
            if reply.get('reply') in del_replies:
                reply['remove'] = True

        self.storage.edit(comment)

        notify(InvalidateCacheEvent(key=self.cacheKey, raw=True))
        return self.redirect(msg=_('Changes saved.'))

    def cancel(self):
        """ Cancel edit
        """
        return self.redirect(to='%s/%s' % (self.context.absolute_url(),
                                           'moderate-inline-comments'))

    def __call__(self, *args, **kwargs):
        method = self.request.method
        if method.lower() != 'post':
            return self.index()

        cancel = self.request.form.pop('form.button.cancel', False)
        if cancel:
            return self.cancel()

        save = self.request.form.pop('form.button.save', False)
        if save:
            return self.save()

        self.redirect()
