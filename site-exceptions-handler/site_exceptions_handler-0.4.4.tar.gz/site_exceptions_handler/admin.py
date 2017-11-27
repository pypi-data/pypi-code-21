# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import SiteExceptionLogger, SiteExceptionLoggerTally
# Register your models here.


class ExceptionTally(admin.TabularInline):
    model = SiteExceptionLoggerTally
    extra = 0
    readonly_fields = [
        'total',
        'created_at',
        'modified_at',
    ]


class ExceptionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_at', 'occurance']
    readonly_fields = [
        'occurance',
        'created_at',
        'modified_at',
        'uid',
        'exception_type',
        'exception_value'
    ]
    exclude = [
        'rendered_html_debug',
        'rendered_html_debug_text',
    ]
    inlines = [
        ExceptionTally,
    ]


admin.site.register(SiteExceptionLogger, ExceptionAdmin)