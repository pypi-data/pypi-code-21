#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .templatetags.jsonify import jsonify


# these are the default settings for the gallery
# change to your needs, if you like to
LIGHTGALLERY_DEFAULT = jsonify(
    {},
    safe=False)


def get_setting(name):
    """
    Return the setting corresponding to the `name` given.
    """
    from django.conf import settings

    default = {
        'LIGHTGALLERY_DEFAULT_OPTIONS':
            getattr(settings, 'LIGHTGALLERY_DEFAULT_OPTIONS', LIGHTGALLERY_DEFAULT),

        'LIGHTGALLERY_ACE_THEME':
            getattr(settings, 'LIGHTGALLERY_ACE_THEME', 'json'),

        'LIGHTGALLERY_ACE_MODE':
            getattr(settings, 'LIGHTGALLERY_ACE_MODE', 'github')
    }
    return default[name]
