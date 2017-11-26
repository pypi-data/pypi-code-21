# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models


class GoogleCalendarPlugin(CMSPluginBase):
    model = models.GoogleCalendar
    name = _('Google Calendar')
    admin_preview = False
    allow_children = False
    render_template = 'djangocms_googlecalendar/index.html'

    fieldsets = [
        (None, {
            'fields': (
                'title',
                ('api_key', 'calendar_id',),
                ('width', 'height',),
            )
        })
    ]

    # def get_render_template(self, context, instance, placeholder):
    #     return 'djangocms_googlecalendar/index.html'.format(instance.template)


plugin_pool.register_plugin(GoogleCalendarPlugin)
