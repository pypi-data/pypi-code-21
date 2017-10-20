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
Email Views
"""

from __future__ import unicode_literals, absolute_import

from rattail import mail
from rattail.db import api
from rattail.config import parse_list

import formalchemy
from formalchemy.helpers import text_area
from pyramid.httpexceptions import HTTPFound
from webhelpers2.html import HTML

from tailbone import forms
from tailbone.db import Session
from tailbone.views import View, MasterView2 as MasterView


class EmailListFieldRenderer(formalchemy.TextAreaFieldRenderer):

    def render(self, **kwargs):
        if isinstance(kwargs.get('size'), tuple):
            kwargs['size'] = 'x'.join([str(i) for i in kwargs['size']])
        value = '\n'.join(parse_list(self.value))
        return text_area(self.name, content=value, **kwargs)


class ProfilesView(MasterView):
    """
    Master view for email admin (settings/preview).
    """
    normalized_model_name = 'emailprofile'
    model_title = "Email Profile"
    model_key = 'key'
    url_prefix = '/email/profiles'
    filterable = False
    pageable = False
    creatable = False
    deletable = False
    grid_columns = [
        'key',
        'prefix',
        'subject',
        'to',
        'enabled',
    ]

    def get_data(self, session=None):
        data = []
        for email in mail.iter_emails(self.rattail_config):
            key = email.key or email.__name__
            email = email(self.rattail_config, key)
            data.append(self.normalize(email))
        return data

    def configure_grid(self, g):
        g.sorters['key'] = g.make_simple_sorter('key', foldcase=True)
        g.sorters['prefix'] = g.make_simple_sorter('prefix', foldcase=True)
        g.sorters['subject'] = g.make_simple_sorter('subject', foldcase=True)
        g.sorters['to'] = g.make_simple_sorter('to', foldcase=True)
        g.sorters['enabled'] = g.make_simple_sorter('enabled')
        g.default_sortkey = 'key'
        g.set_type('enabled', 'boolean')
        g.set_renderer('to', self.render_to)
        g.set_link('key')
        g.set_link('subject')

        # Make edit link visible by default, no "More" actions.
        if g.more_actions:
            g.main_actions.append(g.more_actions.pop())

    def render_to(self, email, column):
        value = email['to']
        if not value:
            return ""
        recips = parse_list(value)
        if len(recips) < 3:
            return value
        return "{}, ...".format(', '.join(recips[:2]))

    def normalize(self, email):
        def get_recips(type_):
            recips = email.get_recips(type_)
            if recips:
                return ', '.join(recips)
        data = email.sample_data(self.request)
        return {
            '_email': email,
            'key': email.key,
            'fallback_key': email.fallback_key,
            'description': email.__doc__,
            'prefix': email.get_prefix(data, magic=False),
            'subject': email.get_subject(data, render=False),
            'sender': email.get_sender(),
            'replyto': email.get_replyto(),
            'to': get_recips('to'),
            'cc': get_recips('cc'),
            'bcc': get_recips('bcc'),
            'enabled': email.get_enabled(),
        }

    def get_instance(self):
        key = self.request.matchdict['key']
        return self.normalize(mail.get_email(self.rattail_config, key))

    def get_instance_title(self, email):
        return email['_email'].get_complete_subject(render=False)

    def editable_instance(self, profile):
        if self.rattail_config.demo():
            return profile['key'] != 'user_feedback'
        return True

    def deletable_instance(self, profile):
        if self.rattail_config.demo():
            return profile['key'] != 'user_feedback'
        return True

    def make_form(self, email, **kwargs):
        """
        Make a simple form for use with CRUD views.
        """
        fs = forms.GenericFieldSet(email)
        fs.append(formalchemy.Field('key', value=email['key'], readonly=True))
        fs.append(formalchemy.Field('fallback_key', value=email['fallback_key'], readonly=True))
        fs.append(formalchemy.Field('description', value=email['description'], readonly=True))
        fs.append(formalchemy.Field('prefix', value=email['prefix'], label="Subject Prefix"))
        fs.append(formalchemy.Field('subject', value=email['subject'], label="Subject Text"))
        fs.append(formalchemy.Field('sender', value=email['sender'], label="From"))
        fs.append(formalchemy.Field('replyto', value=email['replyto'], label="Reply-To"))
        fs.append(formalchemy.Field('to', value=email['to'], renderer=EmailListFieldRenderer, size='60x6'))
        fs.append(formalchemy.Field('cc', value=email['cc'], renderer=EmailListFieldRenderer, size='60x2'))
        fs.append(formalchemy.Field('bcc', value=email['bcc'], renderer=EmailListFieldRenderer, size='60x2'))
        fs.append(formalchemy.Field('enabled', type=formalchemy.types.Boolean, value=email['enabled']))

        form = forms.AlchemyForm(self.request, fs,
                                 creating=self.creating,
                                 editing=self.editing,
                                 action_url=self.request.current_route_url(_query=None),
                                 cancel_url=self.get_action_url('view', email))
        form.readonly = self.viewing
        return form

    def save_form(self, form):
        fs = form.fieldset
        fs.sync()
        key = fs.key._value

        session = Session()
        api.save_setting(session, 'rattail.mail.{}.prefix'.format(key), fs.prefix._value)
        api.save_setting(session, 'rattail.mail.{}.subject'.format(key), fs.subject._value)
        api.save_setting(session, 'rattail.mail.{}.from'.format(key), fs.sender._value)
        api.save_setting(session, 'rattail.mail.{}.replyto'.format(key), fs.replyto._value)
        api.save_setting(session, 'rattail.mail.{}.to'.format(key), (fs.to._value or '').replace('\n', ', '))
        api.save_setting(session, 'rattail.mail.{}.cc'.format(key), (fs.cc._value or '').replace('\n', ', '))
        api.save_setting(session, 'rattail.mail.{}.bcc'.format(key), (fs.bcc._value or '').replace('\n', ', '))
        api.save_setting(session, 'rattail.mail.{}.enabled'.format(key), unicode(fs.enabled._value).lower())

    def template_kwargs_view(self, **kwargs):
        key = self.request.matchdict['key']
        kwargs['email'] = mail.get_email(self.rattail_config, key)
        return kwargs


class EmailPreview(View):
    """
    Lists available email templates, and can show previews of each.
    """

    def __call__(self):

        # Forms submitted via POST are only used for sending emails.
        if self.request.method == 'POST':
            self.email_template()
            return HTTPFound(location=self.request.get_referrer(
                default=self.request.route_url('emailprofiles')))

        # Maybe render a preview?
        key = self.request.GET.get('key')
        if key:
            type_ = self.request.GET.get('type', 'html')
            return self.preview_template(key, type_)

        assert False, "should not be here"

    def email_template(self):
        recipient = self.request.POST.get('recipient')
        if recipient:
            keys = filter(lambda k: k.startswith('send_'), self.request.POST.iterkeys())
            key = keys[0][5:] if keys else None
            if key:
                email = mail.get_email(self.rattail_config, key)
                data = email.sample_data(self.request)
                msg = email.make_message(data)

                subject = msg['Subject']
                del msg['Subject']
                msg['Subject'] = "[preview] {0}".format(subject)

                del msg['To']
                del msg['Cc']
                del msg['Bcc']
                msg['To'] = recipient

                sent = mail.deliver_message(self.rattail_config, key, msg)

                self.request.session.flash("Preview for '{}' was {}emailed to {}".format(
                    key, '' if sent else '(NOT) ', recipient))

    def preview_template(self, key, type_):
        email = mail.get_email(self.rattail_config, key)
        template = email.get_template(type_)
        data = email.sample_data(self.request)
        self.request.response.text = template.render(**data)
        if type_ == 'txt':
            self.request.response.content_type = b'text/plain'
        return self.request.response

    @classmethod
    def defaults(cls, config):
        # email preview
        config.add_route('email.preview', '/email/preview/')
        config.add_view(cls, route_name='email.preview',
                        renderer='/email/preview.mako',
                        permission='emailprofiles.preview')
        config.add_tailbone_permission('emailprofiles', 'emailprofiles.preview',
                                       "Send preview email")



def includeme(config):
    ProfilesView.defaults(config)
    EmailPreview.defaults(config)
