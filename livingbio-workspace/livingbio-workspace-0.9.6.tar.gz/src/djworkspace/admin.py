# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Cache

# Register your models here.


class CacheAdmin(admin.ModelAdmin):
    list_display = ('type', 'key')


admin.site.register(Cache, CacheAdmin)
