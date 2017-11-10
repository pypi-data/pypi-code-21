# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from navsy.forms import PageForm, PatternForm, RouteForm, RouteInlineForm
from navsy.models import Page, Pattern, Route
from navsy.utils import import_function, url_utils
from navsy import settings

if settings.NAVSY_USE_MODELTRANSLATION:
    from modeltranslation.admin import TabbedTranslationAdmin
    __PageAdminBaseClass = TabbedTranslationAdmin
else:
    __PageAdminBaseClass = admin.ModelAdmin


class PatternAdmin(admin.ModelAdmin):

    form = PatternForm
    list_display = ('regex_display', 'regex', )
    list_editable = ('regex', )
    save_on_top = True

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '90'})},
    }

    def get_changelist_form(self, request, **kwargs):
        return PatternForm

admin.site.register(Pattern, PatternAdmin)


class RouteAdmin(admin.ModelAdmin):

    form = RouteForm

    list_display = ('url_display_with_redirect',
                    'view_name', 'view_function_path', 'view_check',
                    'response_type', 'priority', 'published', )
    list_editable = ('view_name', 'view_function_path', 'priority', 'published', )
    save_on_top = True

    def url_display_with_redirect(self, obj):
        html = obj.url_display
        redirect_url = obj.redirect_url
        if redirect_url:
            redirect_label_style = 'color: #AAAAAA; font-weight: normal;'
            redirect_url_style = 'color: #888888; font-weight: normal;'
            html += '<br>&searr; \
                <small style="%s">redirect: </small>\
                <small style="%s">%s</small>\
                ' % (redirect_label_style, redirect_url_style, redirect_url, )
        return html

    url_display_with_redirect.short_description = 'URL Display'
    url_display_with_redirect.allow_tags = True

    def response_type(self, obj):

        badge_style = u'background-color: #CCCCCC; \
                        color: #FFFFFF; \
                        text-transform: uppercase; \
                        padding: 2px 6px; \
                        border-radius: 4px; \
                        margin-right: 5px;'

        badge_format = u'<small style="%s">%s</small>'

        if obj.view_function_path:
            return badge_format % (badge_style, _('function'), )

        elif obj.view_template_path:
            return badge_format % (badge_style, _('template'), )

        elif obj.redirect_url:
            return badge_format % (badge_style, _('redirect'), )
        else:
            return None

    response_type.allow_tags = True
    response_type.short_description = 'Response Type'

    def view_check(self, obj):

        if obj.view_function_path:
            return import_function(obj.view_function_path) is not None

        elif obj.view_template_path:
            try:
                view_template = get_template(obj.view_template_path)
                return True
            except Exception:
                return False

        return None

    view_check.short_description = 'View Check'
    view_check.boolean = True

    def get_fieldsets(self, request, obj=None):

        fieldsets = (
            (None, {
                'classes': ('wide', ),
                'fields': ('page', 'pattern', 'priority', )
            }),
            ('Redirect', {
                'classes': ('wide' if obj and obj.redirect_url else 'collapse', ),
                'fields': (
                    'redirect_to_first_child_page', 'redirect_to_page',
                    'redirect_to_path', 'redirect_to_url',
                )
            }),
            ('View', {
                'classes': ('wide', ),
                'fields': (
                    'view_name', 'view_function_path', 'view_template_path',
                )
            }),
        )

        return fieldsets

    def get_changelist_form(self, request, **kwargs):
        return RouteForm

admin.site.register(Route, RouteAdmin)


class RouteInline(admin.TabularInline):

    model = Route
    form = RouteInlineForm
    fk_name = 'page'
    extra = 0
    fields = ('pattern', 'view_function_path', 'view_name',
              'priority', 'published', 'route_admin_link', )
    readonly_fields = ('route_admin_link', )
    view_on_site = False
    show_change_link = True

    def route_admin_link(self, obj):

        link_style = 'padding:6px 12px; line-height:25px; '

        if obj.id:
            link_href = url_utils.get_admin_change_url(obj)
        else:
            link_href = '#'
            link_style += 'opacity:0.2; pointer-events:none;'

        return u'<a href="%s" target="_self" class="button" style="%s">%s</a>\
                ' % (link_href, link_style, _('Change'), )

    route_admin_link.allow_tags = True
    route_admin_link.short_description = 'Options'


class PageAdmin(__PageAdminBaseClass):

    form = PageForm

    list_display = ('name_with_indentation', 'url_with_link',
                    'home', 'menu', 'priority', 'published', )
    list_display_links = ('name_with_indentation', )
    list_editable = ('home', 'menu', 'priority', 'published', )
    # list_filter = ('menu', )
    list_per_page = 100
    save_on_top = True

    # def name_with_indentation(self, obj):
    #     name = obj.name
    #     indentation_mark = '|____'
    #     indentation_text = [indentation_mark] * obj.parents_count
    #     if indentation_text:
    #         name_padded = u'\
    #         <span style="white-space:nowrap;">\
    #             <span style="padding-left:0px; padding-right:5px; font-weight:normal; font-size:10px;">\
    #                 <span style="color:#EEEEEE;">%s</span>\
    #                 <span style="color:#999999;">%s</span>\
    #             </span> %s\
    #         </span>' % (''.join(indentation_text[0:-1]), indentation_text[-1], name, )
    #         return name_padded
    #     else:
    #         return name

    def name_with_indentation(self, obj):
        name = obj.name
        indentation_mark = '&mdash; '
        indentation_text = indentation_mark * obj.parents_count
        indentation_style = 'padding-left:5px; \
                            padding-right:5px; \
                            font-weight:normal; \
                            color:#999999;'
        if indentation_text:
            name_padded = u'\
            <span style="white-space:nowrap;">\
                <span style="%s">%s</span> %s\
            </span>' % (indentation_style, indentation_text, name, )
            return name_padded
        else:
            return name

    name_with_indentation.short_description = 'Name'
    name_with_indentation.allow_tags = True

    def url_with_link(self, obj):
        obj_url = obj.url
        return u'<a href="%s">%s</a>' % (obj_url, obj_url, )

    url_with_link.short_description = 'URL'
    url_with_link.allow_tags = True

    inlines = [RouteInline]

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':80})},
    }

    def get_changelist_form(self, request, **kwargs):
        return PageForm

    def save_related(self, request, form, formsets, change):
        super(PageAdmin, self).save_related(request, form, formsets, change)
        page_obj = form.instance
        page_obj.create_default_route()

admin.site.register(Page, PageAdmin)
