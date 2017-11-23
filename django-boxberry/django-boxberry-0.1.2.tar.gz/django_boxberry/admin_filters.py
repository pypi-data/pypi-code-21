# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Status, Parsel


class LastStatusLIstFilter(admin.SimpleListFilter):
    title = _('Статусы')
    parameter_name = 'last_status'

    def lookups(self, request, model_admin):
        available_statuses = [(status.id, _(status.name)) for status in Status.objects.all()]
        return set(available_statuses)

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(current_status=Status.objects.filter(id=value).first())
