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
Utilities
"""

from __future__ import unicode_literals, absolute_import

import datetime

import pytz
import humanize

from rattail.time import timezone, make_utc

from webhelpers2.html import HTML, tags


def csrf_token(request, name='_csrf'):
    """
    Convenience function. Returns CSRF hidden tag inside hidden DIV.
    """
    token = request.session.get_csrf_token()
    if token is None:
        token = request.session.new_csrf_token()
    return HTML.tag("div", tags.hidden(name, value=token), style="display:none;")


def pretty_datetime(config, value):
    """
    Formats a datetime as a "pretty" human-readable string, with a tooltip
    showing the ISO string value.

    :param config: Reference to a config object.

    :param value: A ``datetime.datetime`` instance.  Note that if this instance
       is not timezone-aware, its timezone is assumed to be UTC.
    """
    if not value:
        return ''

    # Make sure we're dealing with a tz-aware value.  If we're given a naive
    # value, we assume it to be local to the UTC timezone.
    if not value.tzinfo:
        value = pytz.utc.localize(value)

    # Calculate time diff using UTC.
    time_ago = datetime.datetime.utcnow() - make_utc(value)

    # Convert value to local timezone.
    local = timezone(config)
    value = local.normalize(value.astimezone(local))

    return HTML.tag('span',
                    title=value.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                    c=humanize.naturaltime(time_ago))


def raw_datetime(config, value):
    """
    Formats a datetime as a "raw" human-readable string, with a tooltip
    showing the more human-friendly "time since" equivalent.

    :param config: Reference to a config object.

    :param value: A ``datetime.datetime`` instance.  Note that if this instance
       is not timezone-aware, its timezone is assumed to be UTC.
    """
    if not value:
        return ''

    # Make sure we're dealing with a tz-aware value.  If we're given a naive
    # value, we assume it to be local to the UTC timezone.
    if not value.tzinfo:
        value = pytz.utc.localize(value)

    # Calculate time diff using UTC.
    time_ago = datetime.datetime.utcnow() - make_utc(value)

    # Convert value to local timezone.
    local = timezone(config)
    value = local.normalize(value.astimezone(local))

    kwargs = {}

    # Avoid strftime error when year falls before epoch.
    if value.year >= 1900:
        kwargs['c'] = value.strftime('%Y-%m-%d %I:%M:%S %p')
    else:
        kwargs['c'] = unicode(value)

    # Avoid humanize error when calculating huge time diff.
    if abs(time_ago.days) < 100000:
        kwargs['title'] = humanize.naturaltime(time_ago)

    return HTML.tag('span', **kwargs)
