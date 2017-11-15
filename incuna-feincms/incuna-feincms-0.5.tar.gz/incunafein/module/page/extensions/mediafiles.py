"""
Add a many-to-many relationship field to relate this page to mediafile.mediafile.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms.module.page.models import Page

def register(cls, admin_cls):
    cls.add_to_class('media_files', models.ManyToManyField('medialibrary.MediaFile', blank=True,
        #related_name='%(app_label)s_%(class)s_related',
        null=True, help_text=_('Select media files that should be listed as related content.')))

    try:
        admin_cls.filter_horizontal.append('media_files')
    except AttributeError:
        admin_cls.filter_horizontal = ['media_files']

    admin_cls.fieldsets.append((_('Media Files'), {
        'fields': ('media_files',),
        'classes': ('collapse',),
        }))

