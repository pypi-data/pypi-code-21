# This file is a part of the AnyBlok / Pyramid / Beaker project
#
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration


def beaker_settings(settings):
    """Add in settings the default value for beaker configuration

    :param settings: dict of the existing settings
    """
    settings.update({
        'beaker.session.data_dir': Configuration.get(
            'beaker.session.data_dir'),
        'beaker.session.lock_dir': Configuration.get(
            'beaker.session.lock_dir'),
        'beaker.session.memcache_module': Configuration.get(
            'beaker.session.memcache_module'),
        'beaker.session.type': Configuration.get(
            'beaker.session.type'),
        'beaker.session.url': Configuration.get(
            'beaker.session.url'),
        'beaker.session.cookie_expires': Configuration.get(
            'beaker.session.cookie_expires'),
        'beaker.session.cookie_domain': Configuration.get(
            'beaker.session.cookie_domain'),
        'beaker.session.key': Configuration.get('beaker.session.key'),
        'beaker.session.secret': Configuration.get('beaker.session.secret'),
        'beaker.session.secure': Configuration.get('beaker.session.secure'),
        'beaker.session.timeout': Configuration.get(
            'beaker.session.timeout'),
        'beaker.session.encrypt_key': Configuration.get(
            'beaker.session.encrypt_key'),
        'beaker.session.validate_key': Configuration.get(
            'beaker.session.validate_key'),
    })


def pyramid_beaker(config):
    """Add beaker includeme in pyramid configuration

    :param config: Pyramid configurator instance
    """

    config.include('pyramid_beaker')
