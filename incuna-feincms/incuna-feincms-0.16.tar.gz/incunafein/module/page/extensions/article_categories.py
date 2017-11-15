"""
Add a many-to-many relationship field to relate this page to articles.Article.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms.module.page.models import Page

def register(cls, admin_cls):
    cls.add_to_class('article_categories', models.ManyToManyField('articles.Category', blank=True,
        #related_name='%(app_label)s_%(class)s_related',
        null=True, help_text=_('Select categories that should be listed as related content.')))

    try:
        admin_cls.filter_horizontal.append('article_categories')
    except AttributeError:
        admin_cls.filter_horizontal = ['article_categories']

    title = _('Articles')
    found = False
    for sets in admin_cls.fieldsets:
        if sets[0] == title:
            sets[1]['fields'] = list(sets[1]['fields']) + ['article_categories',]
            found = True
            break

    if not found:
        admin_cls.fieldsets.append((title, {
            'fields': ['article_categories',],
            'classes': ('collapse',),
        }))


