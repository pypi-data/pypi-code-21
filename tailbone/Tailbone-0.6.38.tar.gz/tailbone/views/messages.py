# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Message Views
"""

from __future__ import unicode_literals, absolute_import

import json
import pytz
import six

from rattail import enum
from rattail.db import model
from rattail.time import localtime

import formalchemy
from formalchemy.helpers import text_field
from pyramid import httpexceptions
from webhelpers2.html import tags, HTML

from tailbone import forms
from tailbone.db import Session
from tailbone.views import MasterView2 as MasterView
from tailbone.util import raw_datetime


class SenderFieldRenderer(forms.renderers.UserFieldRenderer):

    def render_readonly(self, **kwargs):
        sender = self.raw_value
        if sender is self.request.user:
            return 'you'
        return super(SenderFieldRenderer, self).render_readonly(**kwargs)


class RecipientsField(formalchemy.Field):
    """
    Custom field for recipients, used when sending new messages.
    """
    is_collection = True

    def sync(self):
        if not self.is_readonly():
            message = self.parent.model
            for uuid in self._deserialize():
                user = Session.query(model.User).get(uuid)
                if user:
                    message.add_recipient(user, status=enum.MESSAGE_STATUS_INBOX)


class RecipientsFieldRenderer(formalchemy.FieldRenderer):

    def render(self, **kwargs):
        uuids = self.value
        value = ','.join(uuids) if uuids else ''
        return text_field(self.name, value=value, **kwargs)

    def deserialize(self):
        value = self.params.getone(self.name).split(',')
        value = [uuid.strip() for uuid in value]
        value = set([uuid for uuid in value if uuid])
        return value

    def render_readonly(self, **kwargs):
        recipients = self.raw_value
        if not recipients:
            return ''
        recips = [r for r in recipients if r.recipient is not self.request.user]
        recips = sorted([r.recipient.display_name for r in recips])
        if len(recips) < len(recipients):
            recips.insert(0, 'you')
        max_display = 5
        if len(recips) > max_display:
            basic = HTML.literal("{}, ".format(', '.join(recips[:max_display-1])))
            more = tags.link_to("({} more)".format(len(recips[max_display-1:])), '#', class_='more')
            everyone = HTML.tag('span', class_='everyone', c=', '.join(recips[max_display-1:]))
            return basic + more + everyone
        return ', '.join(recips)


class MessagesView(MasterView):
    """
    Base class for message views.
    """
    model_class = model.Message
    editable = False
    deletable = False
    checkboxes = True
    replying = False
    reply_header_sent_format = '%a %d %b %Y at %I:%M %p'
    grid_columns = ['subject', 'sender', 'recipients', 'sent']

    def get_index_title(self):
        if self.listing:
            return self.index_title
        if self.viewing:
            message = self.get_instance()
            recipient = self.get_recipient(message)
            if recipient and recipient.status == enum.MESSAGE_STATUS_ARCHIVE:
                return "Message Archive"
            elif not recipient:
                return "Sent Messages"
        return "Message Inbox"

    def get_index_url(self, **kwargs):
        # not really used, but necessary to make certain other code happy
        return self.request.route_url('messages.inbox')

    def index(self):
        if not self.request.user:
            raise httpexceptions.HTTPForbidden
        return super(MessagesView, self).index()

    def get_instance(self):
        if not self.request.user:
            raise httpexceptions.HTTPForbidden
        message = super(MessagesView, self).get_instance()
        if not self.associated_with(message):
            raise httpexceptions.HTTPForbidden
        return message

    def associated_with(self, message):
        if message.sender is self.request.user:
            return True
        for recip in message.recipients:
            if recip.recipient is self.request.user:
                return True
        return False

    def query(self, session):
        return session.query(model.Message)\
                      .outerjoin(model.MessageRecipient)\
                      .filter(model.MessageRecipient.recipient == self.request.user)

    def configure_grid(self, g):
        
        g.joiners['sender'] = lambda q: q.join(model.User, model.User.uuid == model.Message.sender_uuid).outerjoin(model.Person)
        g.filters['sender'] = g.make_filter('sender', model.Person.display_name,
                                            default_active=True, default_verb='contains')
        g.sorters['sender'] = g.make_sorter(model.Person.display_name)

        g.filters['subject'].default_active = True
        g.filters['subject'].default_verb = 'contains'

        g.default_sortkey = 'sent'
        g.default_sortdir = 'desc'

        g.set_renderer('sent', self.render_sent)
        g.set_renderer('sender', self.render_sender)
        g.set_renderer('recipients', self.render_recipients)

        g.set_link('subject')

        g.set_label('sender', "From")
        g.set_label('recipients', "To")

    def render_sent(self, message, column_name):
        return raw_datetime(self.rattail_config, message.sent)

    def render_sender(self, message, column_name):
        sender = message.sender
        if sender is self.request.user:
            return 'you'
        return six.text_type(sender)

    def render_recipients(self, message, column_name):
        recipients = message.recipients
        if recipients:
            recips = [r for r in recipients if r.recipient is not self.request.user]
            recips = sorted([r.recipient.display_name for r in recips])
            if len(recips) < len(recipients) and (
                    message.sender is not self.request.user or not recips):
                recips.insert(0, "you")
            if len(recips) < 5:
                return ", ".join(recips)
            return "{}, ...".format(', '.join(recips[:4]))
        return ""

    def make_form(self, instance, **kwargs):
        form = super(MessagesView, self).make_form(instance, **kwargs)
        if self.creating:
            form.id = 'new-message'
            form.cancel_url = self.request.get_referrer(default=self.request.route_url('messages.inbox'))
            form.create_label = "Send Message"
        return form

    def configure_fieldset(self, fs):
        # TODO: A fair amount of this still seems hacky...

        if self.creating:

            # Must create a new 'sender' field so that we can feed it the
            # current user as default value, but prevent attaching user to the
            # (new) underlying message instance...ugh
            fs.append(formalchemy.Field('sender', value=self.request.user,
                                        renderer=forms.renderers.UserFieldRenderer,
                                        label="From", readonly=True))

            # Sort of the same thing for recipients, although most of that logic is below.
            fs.append(RecipientsField('recipients', label="To", renderer=RecipientsFieldRenderer))

            fs.configure(include=[
                fs.sender,
                fs.recipients,
                fs.subject,
                fs.body.textarea(size='50x15'),
            ])

            # We'll assign some properties directly on the new message;
            # apparently that's safe and won't cause it to be committed.
            # Notably, we can't assign the sender yet.  Also the actual
            # recipients assignment is handled by that field's sync().
            message = fs.model

            if self.replying:
                old_message = self.get_instance()
                message.subject = "Re: {}".format(old_message.subject)
                message.body = self.get_reply_body(old_message)

                # Determine an initial set of recipients, based on reply
                # method.  This value will be set to a 'pseudo' field to avoid
                # touching the new model instance and causing a crap commit.

                # If replying to all, massage the list a little so that the
                # current user is not listed, and the sender is listed first.
                if self.replying == 'all':
                    value = [(r.recipient.uuid, r.recipient.person.display_name)
                             for r in old_message.recipients
                             if self.filter_reply_recipient(r.recipient)]
                    value = dict(value)
                    value.pop(self.request.user.uuid, None)
                    value = sorted(value.iteritems(), key=lambda r: r[1])
                    value = [r[0] for r in value]
                    if old_message.sender is not self.request.user and old_message.sender.active:
                        value.insert(0, old_message.sender_uuid)
                    fs.recipients.set(value=value)

                # Just a normal reply, to sender only.
                elif self.filter_reply_recipient(old_message.sender):
                    fs.recipients.set(value=[old_message.sender.uuid])

                # Set focus to message body instead of recipients, when replying.
                fs.focus = fs.body

        elif self.viewing:

            # Viewing an existing message is a heck of a lot easier...
            fs.configure(include=[
                fs.sender.with_renderer(SenderFieldRenderer).label("From"),
                fs.recipients.with_renderer(RecipientsFieldRenderer).label("To"),
                fs.sent,
                fs.subject,
            ])

    def before_create(self, form):
        """
        This is where we must assign the current user as sender for new
        messages, for now.  I'm still not quite happy with this...
        """
        super(MessagesView, self).before_create(form)
        message = form.fieldset.model
        message.sender = self.request.user

    def flash_after_create(self, obj):
        self.request.session.flash("Message has been sent: {}".format(
            self.get_instance_title(obj)))

    def filter_reply_recipient(self, user):
        return user.active

    def get_reply_header(self, message):
        sent = pytz.utc.localize(message.sent)
        sent = localtime(self.rattail_config, sent)
        sent = sent.strftime(self.reply_header_sent_format)
        return "On {}, {} wrote:".format(sent, message.sender.person.display_name)

    def get_reply_body(self, message):
        """
        Given an original message, this method should return the default body
        value for a "reply" message, i.e. with ">" prefixes etc.
        """
        header = self.get_reply_header(message)
        lines = message.body.split('\n')
        if lines and lines[0]:
            lines.insert(0, '')
        lines = ['', '', '', header] + ["> {}".format(line) for line in lines]
        return '\n'.join(lines)

    def get_recipient(self, message):
        """
        Fetch the recipient from the given message, which corresponds to the
        current (request) user.
        """
        for recipient in message.recipients:
            if recipient.recipient is self.request.user:
                return recipient

    def template_kwargs_create(self, **kwargs):
        kwargs['available_recipients'] = self.get_available_recipients()
        kwargs['json'] = json
        if self.replying:
            kwargs['original_message'] = self.get_instance()
        return kwargs

    def get_available_recipients(self):
        """
        Return the full mapping of recipients which may be included in a
        message sent by the current user.
        """
        recips = {}
        users = Session.query(model.User)\
                       .join(model.Person)\
                       .filter(model.User.active == True)
        for user in users:
            recips[user.uuid] = user.person.display_name
        return recips

    def template_kwargs_view(self, **kwargs):
        message = kwargs['instance']
        return {'message': message,
                'recipient': self.get_recipient(message)}

    def reply(self):
        """
        Reply to a message, i.e. create a new one with first sender as recipient.
        """
        self.replying = True
        return self.create()

    def reply_all(self):
        """
        Reply-all to a message, i.e. create a new one with all original
        recipients listed again in the new message.
        """
        self.replying = 'all'
        return self.create()

    def move(self):
        """
        Move a message, either to the archive or back to the inbox.
        """
        message = self.get_instance()
        recipient = self.get_recipient(message)
        if not recipient:
            raise httpexceptions.HTTPForbidden

        dest = self.request.GET.get('dest')
        if dest not in ('inbox', 'archive'):
            self.request.session.flash("Sorry, I couldn't make sense out of that request.")
            return self.redirect(self.request.get_referrer(
                default=self.request.route_url('messages_inbox')))

        new_status = enum.MESSAGE_STATUS_INBOX if dest == 'inbox' else enum.MESSAGE_STATUS_ARCHIVE
        if recipient.status != new_status:
            recipient.status = new_status
        return self.redirect(self.request.route_url('messages.{}'.format(
            'archive' if dest == 'inbox' else 'inbox')))

    def move_bulk(self):
        """
        Move messages in bulk, to the archive or back to the inbox.
        """
        dest = self.request.POST.get('destination', 'archive')
        if self.request.method == 'POST':
            uuids = self.request.POST.get('uuids', '').split(',')
            if uuids:
                new_status = enum.MESSAGE_STATUS_INBOX if dest == 'inbox' else enum.MESSAGE_STATUS_ARCHIVE
                for uuid in uuids:
                    recip = self.Session.query(model.MessageRecipient)\
                                        .filter(model.MessageRecipient.message_uuid == uuid)\
                                        .filter(model.MessageRecipient.recipient_uuid == self.request.user.uuid)\
                                        .first()
                    if recip and recip.status != new_status:
                        recip.status = new_status
        route = 'messages.{}'.format('archive' if dest == 'inbox' else 'inbox')
        return self.redirect(self.request.route_url(route))

    @classmethod
    def defaults(cls, config):
        """
        Extra default config for message views.
        """

        # reply
        config.add_route('messages.reply', '/messages/{uuid}/reply')
        config.add_view(cls, attr='reply', route_name='messages.reply',
                        permission='messages.create')

        # reply-all
        config.add_route('messages.reply_all', '/messages/{uuid}/reply-all')
        config.add_view(cls, attr='reply_all', route_name='messages.reply_all',
                        permission='messages.create')

        # move (single)
        config.add_route('messages.move', '/messages/{uuid}/move')
        config.add_view(cls, attr='move', route_name='messages.move')

        # move bulk
        config.add_route('messages.move_bulk', '/messages/move-bulk')
        config.add_view(cls, attr='move_bulk', route_name='messages.move_bulk')

        cls._defaults(config)


class InboxView(MessagesView):
    """
    Inbox message view.
    """
    url_prefix = '/messages/inbox'
    grid_key = 'messages.inbox'
    index_title = "Message Inbox"

    def get_index_url(self, **kwargs):
        return self.request.route_url('messages.inbox')

    def query(self, session):
        q = super(InboxView, self).query(session)
        return q.filter(model.MessageRecipient.status == enum.MESSAGE_STATUS_INBOX)


class ArchiveView(MessagesView):
    """
    Archived message view.
    """
    url_prefix = '/messages/archive'
    grid_key = 'messages.archive'
    index_title = "Message Archive"

    def get_index_url(self, **kwargs):
        return self.request.route_url('messages.archive')

    def query(self, session):
        q = super(ArchiveView, self).query(session)
        return q.filter(model.MessageRecipient.status == enum.MESSAGE_STATUS_ARCHIVE)


class SentView(MessagesView):
    """
    Sent messages view.
    """
    url_prefix = '/messages/sent'
    grid_key = 'messages.sent'
    checkboxes = False
    index_title = "Sent Messages"

    def get_index_url(self, **kwargs):
        return self.request.route_url('messages.sent')

    def query(self, session):
        return session.query(model.Message)\
                      .filter(model.Message.sender == self.request.user)

    def configure_grid(self, g):
        super(SentView, self).configure_grid(g)
        g.filters['sender'].default_active = False
        g.joiners['recipients'] = lambda q: q.join(model.MessageRecipient)\
                                             .join(model.User, model.User.uuid == model.MessageRecipient.recipient_uuid)\
                                             .join(model.Person)
        g.filters['recipients'] = g.make_filter('recipients', model.Person.display_name,
                                                default_active=True, default_verb='contains')


def includeme(config):

    config.add_tailbone_permission('messages', 'messages.list', "List/Search Messages")

    # inbox
    config.add_route('messages.inbox', '/messages/inbox/')
    config.add_view(InboxView, attr='index', route_name='messages.inbox',
                    permission='messages.list')

    # archive
    config.add_route('messages.archive', '/messages/archive/')
    config.add_view(ArchiveView, attr='index', route_name='messages.archive',
                    permission='messages.list')

    # sent
    config.add_route('messages.sent', '/messages/sent/')
    config.add_view(SentView, attr='index', route_name='messages.sent',
                    permission='messages.list')

    MessagesView.defaults(config)
