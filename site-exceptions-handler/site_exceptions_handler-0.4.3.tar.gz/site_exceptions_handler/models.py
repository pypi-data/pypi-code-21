# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from .mixims import Timestamps
from jsonfield import JSONField
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _

from . import states

ALL_STATES = sorted(states.ALL_STATES)

# Create your models here.

AUTH_USER_MODEL = settings.AUTH_USER_MODEL


class SiteExceptionLogger(Timestamps):
    uid = models.UUIDField(null=True, blank=True, auto_created=True)
    occurance = models.BigIntegerField(null=True, default=1)
    exception_type = models.CharField(max_length=225, null=True, blank=True)
    exception_value = models.CharField(max_length=1000, null=True, blank=True)

    exception_traceback_json = JSONField(null=True, blank=True)

    rendered_html_debug = models.TextField(blank=True, null=True)
    rendered_html_debug_text = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-modified_at',)
        verbose_name = _('Exception')
        verbose_name_plural = _('Exceptions')

    def to_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'occurance': self.occurance,
            'exception_type': self.exception_type,
            'exception_value': self.exception_value
        }

    def __str__(self):
        return '{0.uid} - {0.exception_value}'.format(self)


class SiteExceptionLoggerTally(Timestamps):
    exception = models.ForeignKey(SiteExceptionLogger, on_delete=models.CASCADE)
    total = models.BigIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('Exception Tally')
        verbose_name_plural = _('Exceptions Tally')

    def to_dict(self):
        return {
            'exception': self.exception,
            'total': self.total,
            'created_at': self.created_at,
            'modified_at': self.modified_at
        }

    def __str__(self):
        return '{0.exception.exception_value} - Total: {0.total}'.format(self)