# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin

from models import *

# Register your models here.

class ContactAdmin(admin.ModelAdmin):
    model = Contact
    list_display = ('name', 'email', 'subject')
    list_display_links = ('name', 'email', 'subject')

class gTitleInline(NestedStackedInline):
    model = gTitle
    extra = 0
    fk_name = 'component'

class gTextboxInline(NestedStackedInline):
    model = gTextbox
    extra = 0
    fk_name = 'component'

class ComponentInline(NestedStackedInline):
    model = Component
    extra = 1
    fk_name = 'page'
    inlines = [
        gTitleInline,
        gTextboxInline
    ]

class PageAdmin(NestedModelAdmin):
    model = Page
    # list_display = ("components",)
    # list_display_links = list_display
    list_display = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name',),
        }),
    )
    inlines = [
        ComponentInline,
    ]

admin.site.register(Page, PageAdmin)
admin.site.register(Contact, ContactAdmin)
