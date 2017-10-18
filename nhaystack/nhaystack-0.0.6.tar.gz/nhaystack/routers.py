# coding: utf-8

from __future__ import absolute_import

from django.conf import settings
from django.utils.translation import get_language

from haystack import routers
from haystack.constants import DEFAULT_ALIAS


class LanguageRouter(routers.BaseRouter):
    def for_read(self, **hints):
        language = get_language()
        if language in settings.HAYSTACK_CONNECTIONS:
            return language
        return DEFAULT_ALIAS

    for_write = for_read
