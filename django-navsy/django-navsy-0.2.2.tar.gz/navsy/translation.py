# -*- coding: utf-8 -*-

from navsy import settings
from navsy.models import Page


if settings.NAVSY_MULTILANGUAGE:

    from modeltranslation.translator import translator, TranslationOptions

    class PageTranslationOptions(TranslationOptions):
        fields = ('name', 'slug', )

    translator.register(Page, PageTranslationOptions)
