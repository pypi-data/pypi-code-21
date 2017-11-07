from django.contrib import admin

from pages.models.page import Page, PageSEO, PageTag, PageTimer
from pages.utils.constants import PAGE_CUSTOM_ADMIN
from pages.models.slider import Slider, SliderContent, SliderItem, SliderContentType


class PageTimerAdmin(admin.ModelAdmin):
    model = PageTimer
    list_display = ('identifier', 'title', 'expire_date', 'created', 'modified')
    list_filter = ('is_active', )
    search_fields = ('identifier', 'title', 'expire_date')


class PageSEOAdmin(admin.ModelAdmin):
    model = PageSEO
    list_display = ('title', 'description', 'slug', 'keywords', 'banner_share')


class PageAdmin(admin.ModelAdmin):
    list_display = ['description', 'external_url', 'is_active', 'created']
    exclude = ['created', 'updated']
    search_fields = ('descrition', 'title', 'subtitle')


class SliderAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created']
    list_filter = ['page', 'is_active']
    exclude = ['created', 'updated']
    search_fields = ('title', )


class SliderItemAdmin(admin.ModelAdmin):
    list_display = ['slider', 'active_from', 'active_to', 'is_active', 'created']
    exclude = ['created', 'updated']
    list_filter = ['slider', 'is_active']


class SliderContentTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


class SliderContentAdmin(admin.ModelAdmin):
    list_display = ['order', 'type_content']


if not PAGE_CUSTOM_ADMIN:
    admin.site.register(Page, PageAdmin)

admin.site.register(Slider, SliderAdmin)
admin.site.register(SliderItem, SliderItemAdmin)
admin.site.register(SliderContent, SliderContentAdmin)
admin.site.register(SliderContentType, SliderContentTypeAdmin)
admin.site.register(PageSEO, PageSEOAdmin)
admin.site.register(PageTimer, PageTimerAdmin)
