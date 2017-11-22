#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import LightGalleryImage
from .settings import get_setting

admin.site.register(LightGalleryImage)


class LightGalleryAceMixin:
    change_form_template = 'djangocms_lightgallery/change_form.html'
    text_area_attrs = {
        'rows': 20,
        'data-editor': True,
        'data-mode': get_setting('LIGHTGALLERY_ACE_THEME'),
        'data-theme': get_setting('LIGHTGALLERY_ACE_MODE'),
    }

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs=text_area_attrs)}
    }
