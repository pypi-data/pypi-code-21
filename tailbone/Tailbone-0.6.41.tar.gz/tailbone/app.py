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
Application Entry Point
"""

from __future__ import unicode_literals, absolute_import

import os
import warnings

import sqlalchemy as sa

import rattail.db
from rattail.config import make_config
from rattail.exceptions import ConfigurationError
from rattail.db.config import get_engines, configure_versioning
from rattail.db.types import GPCType

import formalchemy as fa
from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy

import tailbone.db
from tailbone.auth import TailboneAuthorizationPolicy


def make_rattail_config(settings):
    """
    Make a Rattail config object from the given settings.
    """
    rattail_config = settings.get('rattail_config')
    if not rattail_config:

        # initialize rattail config and embed in settings dict, to make
        # available for web requests later
        path = settings.get('rattail.config')
        if not path or not os.path.exists(path):
            path = settings.get('edbob.config')
            if not path or not os.path.exists(path):
                raise ConfigurationError("Please set 'rattail.config' in [app:main] section of config "
                                         "to the path of your config file.  Lame, but necessary.")
            warnings.warn("[app:main] setting 'edbob.config' is deprecated; "
                          "please use 'rattail.config' setting instead",
                          DeprecationWarning)
        rattail_config = make_config(path)
        settings['rattail_config'] = rattail_config
    rattail_config.configure_logging()

    rattail_engines = settings.get('rattail_engines')
    if not rattail_engines:

        # Load all Rattail database engines from config, and store in settings
        # dict.  This is necessary e.g. in the case of a host server, to have
        # access to its subordinate store servers.
        rattail_engines = get_engines(rattail_config)
        settings['rattail_engines'] = rattail_engines

    # Configure the database session classes.  Note that most of the time we'll
    # be using the Tailbone Session, but occasionally (e.g. within batch
    # processing threads) we want the Rattail Session.  The reason is that
    # during normal request processing, the Tailbone Session is preferable as
    # it includes Zope Transaction magic.  Within an explicitly-spawned thread
    # however, this is *not* desirable.
    rattail.db.Session.configure(bind=rattail_engines['default'])
    tailbone.db.Session.configure(bind=rattail_engines['default'])
    if hasattr(rattail_config, 'tempmon_engine'):
        tailbone.db.TempmonSession.configure(bind=rattail_config.tempmon_engine)
    if hasattr(rattail_config, 'trainwreck_engine'):
        tailbone.db.TrainwreckSession.configure(bind=rattail_config.trainwreck_engine)

    # Make sure rattail config object uses our scoped session, to avoid
    # unnecessary connections (and pooling limits).
    rattail_config._session_factory = lambda: (tailbone.db.Session(), False)

    # Configure (or not) Continuum versioning.
    configure_versioning(rattail_config)
    return rattail_config


def provide_postgresql_settings(settings):
    """
    Add some PostgreSQL-specific settings to the app config.  Specifically,
    this enables retrying transactions a second time, in an attempt to
    gracefully handle database restarts.
    """
    settings.setdefault('tm.attempts', 2)


class Root(dict):
    """
    Root factory for Pyramid.  This is necessary to make the current request
    available to the authorization policy object, which needs it to check if
    the current request "is root".
    """

    def __init__(self, request):
        self.request = request


def make_pyramid_config(settings, configure_csrf=True):
    """
    Make a Pyramid config object from the given settings.
    """
    from tailbone.forms.alchemy import TemplateEngine
    from tailbone.forms import renderers

    config = settings.pop('pyramid_config', None)
    if config:
        config.set_root_factory(Root)
    else:
        settings.setdefault('pyramid_deform.template_search_path', 'tailbone:templates/deform')
        config = Configurator(settings=settings, root_factory=Root)

    # configure user authorization / authentication
    config.set_authorization_policy(TailboneAuthorizationPolicy())
    config.set_authentication_policy(SessionAuthenticationPolicy())

    # always require CSRF token protection
    if configure_csrf:
        config.set_default_csrf_options(require_csrf=True, token='_csrf')

    # Bring in some Pyramid goodies.
    config.include('tailbone.beaker')
    config.include('pyramid_deform')
    config.include('pyramid_mako')
    config.include('pyramid_tm')

    # Add some permissions magic.
    config.add_directive('add_tailbone_permission_group', 'tailbone.auth.add_permission_group')
    config.add_directive('add_tailbone_permission', 'tailbone.auth.add_permission')

    # TODO: This can finally be removed once all CRUD/index views have been
    # converted to use the new master view etc.
    for label, perms in settings.get('edbob.permissions', []):
        groupkey = label.lower().replace(' ', '_')
        config.add_tailbone_permission_group(groupkey, label)
        for key, label in perms:
            config.add_tailbone_permission(groupkey, key, label)

    # Configure FormAlchemy.
    fa.config.engine = TemplateEngine()
    fa.FieldSet.default_renderers[sa.Boolean] = renderers.YesNoFieldRenderer
    fa.FieldSet.default_renderers[sa.Date] = renderers.DateFieldRenderer
    fa.FieldSet.default_renderers[sa.DateTime] = renderers.DateTimeFieldRenderer
    fa.FieldSet.default_renderers[sa.Time] = renderers.TimeFieldRenderer
    fa.FieldSet.default_renderers[GPCType] = renderers.GPCFieldRenderer

    return config


def configure_postgresql(pyramid_config):
    """
    Add some PostgreSQL-specific tweaks to the final app config.  Specifically,
    adds the tween necessary for graceful handling of database restarts.
    """
    pyramid_config.add_tween('tailbone.tweens.sqlerror_tween_factory',
                             under='pyramid_tm.tm_tween_factory')


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    settings.setdefault('mako.directories', ['tailbone:templates'])
    rattail_config = make_rattail_config(settings)
    pyramid_config = make_pyramid_config(settings)
    pyramid_config.include('tailbone')
    return pyramid_config.make_wsgi_app()
