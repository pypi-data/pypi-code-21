# -*- coding: utf-8 -*-
"""
Enables the user to add a google calendar.
"""
from __future__ import unicode_literals

import re
import json

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _

from cms.models import CMSPlugin


CSS_WIDTH_RE = re.compile(r'^\d+(?:px|%)$')
CSS_HEIGHT_RE = re.compile(r'^\d+px$')


@python_2_unicode_compatible
class GoogleCalendar(CMSPlugin):
    """
    Renders the Google Calendar wrapper
    """
    title = models.CharField(
        verbose_name=_('Calendar title'),
        max_length=255,
        blank=True,
    )
    api_key = models.CharField(
        verbose_name=_('Google Calendar API Key'),
        max_length=255,
    )
    calendar_id = models.CharField(
        verbose_name=_('Google Calendar ID'),
        max_length=255,
    )
    width = models.CharField(
        verbose_name=_('Width'),
        max_length=6,
        default='100%',
        help_text=_('Width of the calendar, including the CSS length units (e.g. "100%", "400px" or "400rem").'),
    )
    height = models.CharField(
        verbose_name=_('Height'),
        max_length=6,
        default='400px',
        help_text=_('Height of the calendar, including the CSS length units (e.g. "400px" or "400rem").'),
    )

    # Add an app namespace to related_name to avoid field name clashes
    # with any other plugins that have a field with the same name as the
    # lowercase of the class name of this model.
    # https://github.com/divio/django-cms/issues/5030
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin,
        related_name='%(app_label)s_%(class)s',
        parent_link=True,
    )

    def __str__(self):
        if self.title:
            return self.title
        return str(self.pk)

    def get_short_description(self):
        display = ''
        if self.title:
            display = '{0}, '.format(self.title)
        display += '{0} x {1}'.format(self.width, self.height)
        return display

    def clean(self):
        if self.width and not CSS_WIDTH_RE.match(self.width):
            raise ValidationError(
                _('Width must be a positive integer followed by "px" or "%".')
            )
        if self.height and not CSS_HEIGHT_RE.match(self.height):
            raise ValidationError(
                _('Height must be a positive integer followed by "px".')
            )
