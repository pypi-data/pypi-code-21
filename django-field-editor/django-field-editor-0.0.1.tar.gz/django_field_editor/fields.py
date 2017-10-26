# -*- coding: utf-8 -*-

from django.contrib.postgres import forms as django_postgres_forms

from .widgets import JsonEditorWidget


class DjangoPostgersJsonField(django_postgres_forms.JSONField):
    """Rewrite JSONField"""

    widget = JsonEditorWidget
