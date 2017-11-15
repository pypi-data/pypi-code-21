"""
Add a many-to-many relationship field to relate this page to links.Link.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms.module.page.models import Page

def register(cls, admin_cls):
    cls.add_to_class('links', models.ManyToManyField('links.Link', blank=True,
        #related_name='%(app_label)s_%(class)s_related',
        null=True, help_text=_('Select links that should be listed as related content.')))

    try:
        admin_cls.filter_horizontal.append('links')
    except AttributeError:
        admin_cls.filter_horizontal = ['links']

    admin_cls.fieldsets.append((_('Links'), {
        'fields': ('links',),
        'classes': ('collapse',),
        }))

