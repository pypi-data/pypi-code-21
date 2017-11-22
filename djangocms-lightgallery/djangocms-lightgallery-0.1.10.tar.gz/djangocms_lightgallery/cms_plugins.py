# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .admin import LightGalleryAceMixin
from .models import LightGallery, LightGalleryImage


class LightGalleryImageInline(admin.TabularInline):
    model = LightGalleryImage
    extra = 1


@plugin_pool.register_plugin
class LightGalleryPlugin(LightGalleryAceMixin, CMSPluginBase):
    """
    The main LightGallery Plugin. Here, we can define various settings
    and behavior of the plugin.

    This Plugin adds a LightGallery Plugin to Django CMS. You can add
    images as inline objects. The images will be rendered as thumbnails.
    """
    model = LightGallery
    name = _('Light Gallery')
    render_template = 'djangocms_lightgallery/base.html'
    cache = False
    inlines = [LightGalleryImageInline, ]

    def render(self, context, instance, placeholder):
        context = super(LightGalleryPlugin, self).render(
            context, instance, placeholder)

        # define context vars
        context.update({
            'images': instance.images.all(),
        })

        return context
