
from django.contrib import admin

from trans.admin import TranslationAdmin

from seo.models import PageMeta


class PageMetaAdmin(TranslationAdmin):

    list_display = ['url', 'title', 'robots', 'site']
    list_filter = ['site']
    list_editable = ['robots']


admin.site.register(PageMeta, PageMetaAdmin)
