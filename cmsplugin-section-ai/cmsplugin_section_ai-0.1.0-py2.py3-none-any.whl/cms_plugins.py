# -*- coding: utf-8 -*-
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Section, SectionButton


class SectionButtonAdmin(admin.StackedInline):
    model = SectionButton
    extra = 1


class SectionPlugin(CMSPluginBase):
    model = Section
    name = _("Section")
    inlines = (SectionButtonAdmin,)
    allow_children = True
    render_template = "cmsplugin_section_ai/section.html"

    def render(self, context, instance, placeholder):
        context["section"] = instance
        return context


plugin_pool.register_plugin(SectionPlugin)
