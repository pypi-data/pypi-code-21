# -*- coding: utf-8 -*-

import django

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if django.VERSION < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

from navsy.exceptions import NoReverseMatch


NAVSY_MULTILANGUAGE = bool(len(settings.LANGUAGES) > 1)
NAVSY_USE_MODELTRANSLATION = False

if NAVSY_MULTILANGUAGE and 'modeltranslation' in settings.INSTALLED_APPS:
    try:
        import modeltranslation
        NAVSY_USE_MODELTRANSLATION = True
    except ImportError:
        pass


def check_settings():

    # TODO: check if 'navsy.context_processors.data' is added to
    # CONTEXT_PROCESSORS

    try:
        reverse('navsy-router')
    except NoReverseMatch:
        e = 'You must add "'
        e += 'url(r\'^\', include(\'navsy.urls\'))'
        e += '" to your urls.'
        raise ImproperlyConfigured(e)

    if NAVSY_MULTILANGUAGE:
        try:
            reverse('set_language')
        except NoReverseMatch:
            e = 'You must add "'
            e += 'url(r\'^i18n/\', include(\'django.conf.urls.i18n\'))'
            e += '" to your urls.'
            raise ImproperlyConfigured(e)
