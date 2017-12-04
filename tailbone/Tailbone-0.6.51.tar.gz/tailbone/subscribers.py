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
Event Subscribers
"""

from __future__ import unicode_literals, absolute_import

import six
import json

import rattail
from rattail.db import model
from rattail.db.auth import has_permission

from pyramid import threadlocal

import tailbone
from tailbone import helpers
from tailbone.db import Session


def add_rattail_config_attribute_to_request(event):
    """
    Add a ``rattail_config`` attribute to a request object.

    This function is really just a matter of convenience, but it should help to
    make other code more terse (example below).  It is designed to act as a
    subscriber to the Pyramid ``NewRequest`` event.

    A global Rattail ``config`` should already be present within the Pyramid
    application registry's settings, which would normally be accessed via::
    
       request.registry.settings['rattail_config']

    This function merely "promotes" this config object so that it is more
    directly accessible, a la::

       request.rattail_config

    .. note::
       All this of course assumes that a Rattail ``config`` object *has* in
       fact already been placed in the application registry settings.  If this
       is not the case, this function will do nothing.
    """
    request = event.request
    rattail_config = request.registry.settings.get('rattail_config')
    if rattail_config:
        request.rattail_config = rattail_config


def before_render(event):
    """
    Adds goodies to the global template renderer context.
    """

    request = event.get('request') or threadlocal.get_current_request()

    renderer_globals = event
    renderer_globals['h'] = helpers
    renderer_globals['url'] = request.route_url
    renderer_globals['rattail'] = rattail
    renderer_globals['tailbone'] = tailbone
    renderer_globals['enum'] = request.rattail_config.get_enum()
    renderer_globals['six'] = six
    renderer_globals['json'] = json


def add_inbox_count(event):
    """
    Adds the current user's inbox message count to the global renderer context.

    Note that this is not enabled by default; to turn it on you must do this:

       config.add_subscriber('tailbone.subscribers.add_inbox_count', 'pyramid.events.BeforeRender')
    """
    request = event.get('request') or threadlocal.get_current_request()
    if request.user:
        renderer_globals = event
        enum = request.rattail_config.get_enum()
        renderer_globals['inbox_count'] = Session.query(model.Message)\
                                                 .outerjoin(model.MessageRecipient)\
                                                 .filter(model.MessageRecipient.recipient == Session.merge(request.user))\
                                                 .filter(model.MessageRecipient.status == enum.MESSAGE_STATUS_INBOX)\
                                                 .count()


def context_found(event):
    """
    Attach some goodies to the request object.

    The following is attached to the request:

    * The currently logged-in user instance (if any), as ``user``.

    * ``is_admin`` flag indicating whether user has the Administrator role.

    * ``is_root`` flag indicating whether user is currently elevated to root.

    * A shortcut method for permission checking, as ``has_perm()``.

    * A shortcut method for fetching the referrer, as ``get_referrer()``.
    """

    request = event.request

    request.user = None
    uuid = request.authenticated_userid
    if uuid:
        request.user = Session.query(model.User).get(uuid)
        if request.user:
            Session().set_continuum_user(request.user)

    request.is_admin = bool(request.user) and request.user.is_admin()
    request.is_root = request.is_admin and request.session.get('is_root', False)

    def has_perm(name):
        if has_permission(Session(), request.user, name):
            return True
        return request.is_root
    request.has_perm = has_perm

    def has_any_perm(*names):
        for name in names:
            if has_perm(name):
                return True
        return False
    request.has_any_perm = has_any_perm

    def get_referrer(default=None):
        if request.params.get('referrer'):
            return request.params['referrer']
        if request.session.get('referrer'):
            return request.session.pop('referrer')
        referrer = request.referrer
        if (not referrer or referrer == request.current_route_url()
            or not referrer.startswith(request.host_url)):
            referrer = default or request.route_url('home')
        return referrer
    request.get_referrer = get_referrer

    def get_session_timeout():
        """
        Returns the timeout in effect for the current session
        """
        return request.session.get('_timeout')
    request.get_session_timeout = get_session_timeout


def includeme(config):
    config.add_subscriber(add_rattail_config_attribute_to_request, 'pyramid.events.NewRequest')
    config.add_subscriber(before_render, 'pyramid.events.BeforeRender')
    config.add_subscriber(context_found, 'pyramid.events.ContextFound')
