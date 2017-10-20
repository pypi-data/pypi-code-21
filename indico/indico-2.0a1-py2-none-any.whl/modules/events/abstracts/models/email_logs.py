# This file is part of Indico.
# Copyright (C) 2002 - 2017 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from sqlalchemy.dialects.postgresql import ARRAY, JSON

from indico.core.db.sqlalchemy import UTCDateTime, db
from indico.util.date_time import now_utc
from indico.util.string import format_repr, return_ascii


class AbstractEmailLogEntry(db.Model):
    __tablename__ = 'email_logs'
    __table_args__ = {'schema': 'event_abstracts'}

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    abstract_id = db.Column(
        db.Integer,
        db.ForeignKey('event_abstracts.abstracts.id'),
        index=True,
        nullable=False
    )
    email_template_id = db.Column(
        db.Integer,
        db.ForeignKey('event_abstracts.email_templates.id'),
        index=True,
        nullable=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.users.id'),
        index=True,
        nullable=True
    )
    sent_dt = db.Column(
        UTCDateTime,
        nullable=False,
        default=now_utc
    )
    recipients = db.Column(
        ARRAY(db.String),
        nullable=False
    )
    subject = db.Column(
        db.String,
        nullable=False
    )
    body = db.Column(
        db.Text,
        nullable=False
    )
    data = db.Column(
        JSON,
        nullable=False
    )

    abstract = db.relationship(
        'Abstract',
        lazy=True,
        backref=db.backref(
            'email_logs',
            order_by=sent_dt,
            lazy=True,
            cascade='all, delete-orphan'
        )
    )
    email_template = db.relationship(
        'AbstractEmailTemplate',
        lazy=True,
        backref=db.backref(
            'logs',
            lazy='dynamic'
        )
    )
    user = db.relationship(
        'User',
        lazy=True,
        backref=db.backref(
            'abstract_email_log_entries',
            lazy='dynamic'
        )
    )

    @return_ascii
    def __repr__(self):
        return format_repr(self, 'id', 'abstract_id', _text=self.subject)

    @classmethod
    def create_from_email(cls, email_data, email_tpl, user=None):
        """Create a new log entry from the data used to send an email

        :param email_data: email data as returned from `make_email`
        :param email_tpl: the abstract email template that created the
                          email
        :param user: the user who performed the action causing the
                     notification
        """
        recipients = sorted(email_data['toList'] | email_data['ccList'] | email_data['bccList'])
        data = {'template_name': email_tpl.title}
        return cls(email_template=email_tpl, user=user, recipients=recipients, subject=email_data['subject'],
                   body=email_data['body'], data=data)
