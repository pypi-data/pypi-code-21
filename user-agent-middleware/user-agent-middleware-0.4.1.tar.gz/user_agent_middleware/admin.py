from __future__ import unicode_literals

from django.contrib import admin

from .models import Visitor
# Register your models here.


class VisitorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'visit_datetime', 'ipaddress']
    readonly_fields = ['visit_datetime']