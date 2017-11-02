# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.utils.html import mark_safe

from glitter import block_admin
from glitter.admin import GlitterAdminMixin

from .models import Category, Document, Format, LatestDocumentsBlock


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    search_fields = ('title', )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('title', )
    prepopulated_fields = {'slug': ('title', 'parent_category')}

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        qs = form.base_fields['parent_category'].queryset
        # To restrict to only 1 level of dependency we do the following:
        # - Only show categories that have no parents themselves.
        qs = qs.filter(parent_category__isnull=True)

        if obj:
            if obj.category_set.all().exists():
                # If this category is a parent, it can not have a parent.
                qs = Category.objects.none()
            else:
                # Exclude itself, you can't be your own parent.
                qs = qs.exclude(pk=obj.pk)

        form.base_fields['parent_category'].queryset = qs

        return form


@admin.register(Document)
class DocumentAdmin(GlitterAdminMixin, admin.ModelAdmin):
    date_hierarchy = 'publish_at'
    raw_id_fields = ('image',)
    list_display = (
        'title', 'category', 'document_format', 'file_size', 'view_on_site_link', 'publish_at',
        'is_published',
    )
    list_filter = ('category', )
    prepopulated_fields = {'slug': ('title', )}

    def get_inline_instances(self, request, obj=None):
        # Optional glitter applications. Both are imported after the is_installed check to prevent
        # migrations applied to the core glitter app
        if apps.is_installed('glitter.publisher'):
            from glitter.publisher.admin import ActionInline
            if ActionInline not in self.inlines:
                self.inlines = self.inlines + [ActionInline]

        if apps.is_installed('glitter.reminders'):
            from glitter.reminders.admin import ReminderInline
            if ReminderInline not in self.inlines:
                self.inlines = self.inlines + [ReminderInline]

        return super(DocumentAdmin, self).get_inline_instances(request, obj)

    def get_fieldsets(self, request, obj=None):
        advanced_options = ['slug', 'tags', 'image', 'publish_at']
        if not getattr(settings, 'GLITTER_DOCUMENTS_TAGS', False):
            advanced_options.remove('tags')

        fieldsets = ((
            'Document', {
                'fields': (
                    'title', 'category', 'author', 'document', 'document_format', 'summary',
                )
            }
        ), ('Advanced options', {'fields': advanced_options}), )
        return fieldsets

    def view_on_site_link(self, obj):
        link_html = '<a href="{url}">View document</a>'.format(url=obj.get_absolute_url())
        return mark_safe(link_html)

    view_on_site_link.short_description = 'View document'


block_admin.site.register(LatestDocumentsBlock)
block_admin.site.register_block(LatestDocumentsBlock, 'App Blocks')
