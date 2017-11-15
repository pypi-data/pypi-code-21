from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from .models import XLSImportProfile, XLSColumn, XLSPriceList, XLSImportHistory
from .forms import XLSImportProfileForm


class XLSColumnInline(admin.TabularInline):
    model = XLSColumn
    extra = 1


class XLSImportProfileAdmin(admin.ModelAdmin):
    list_display = ('title', 'default_product_type', 'default_collection', 'first_row_as_labels', 'added')
    search_fields = ('title',)
    date_hierarchy = 'added'
    form = XLSImportProfileForm
    inlines = [XLSColumnInline]
    raw_id_fields = ('default_product_type', 'default_collection')

admin.site.register(XLSImportProfile, XLSImportProfileAdmin)


class XLSPriceListAdmin(admin.ModelAdmin):
    list_display = ('profile', 'status', 'added', 'preview_link')
    list_filter = ('status',)
    date_hierarchy = 'added'
    actions = ['process_action']

    def preview_link(self, obj):
        from django.urls import reverse
        if obj:
            url = reverse('admin:price_list_preview', args=[obj.pk])
            return mark_safe('<a href="%s" class="button" target="_blank">Preview</a>' % url)
        else:
            return ''

    def price_list_preview(self, request, id):
        from django.template.response import TemplateResponse
        from django.shortcuts import get_object_or_404
        price_list = get_object_or_404(XLSPriceList, pk=id)

        limit = int(request.GET.get('limit', 50))
        result, meta = price_list.load_data(limit=limit)

        context = dict(
            self.admin_site.each_context(request),
        )
        context.update({
            'opts': self.model._meta,
            'module_name': self.model._meta.verbose_name_plural.title(),
            'object': price_list,
            'title': _('Price list preview'),
            'result': result,
            'meta': meta,
        })
        return TemplateResponse(request, "admin/pcart_import/xlspricelist/preview.html", context)

    def get_urls(self):
        from django.conf.urls import url
        urls = super(XLSPriceListAdmin, self).get_urls()
        my_urls = [
            url(
                r'^(.+)/preview/$',
                self.admin_site.admin_view(self.price_list_preview),
                name='price_list_preview',
            ),
        ]
        return my_urls + urls

    def process_action(self, request, queryset):
        from .tasks import import_xls_price_list
        for q in queryset:
            import_xls_price_list.delay(q.pk)
    process_action.short_description = _('Process')

admin.site.register(XLSPriceList, XLSPriceListAdmin)


class XLSImportHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'success', 'added')
    date_hierarchy = 'added'
    search_fields = ('message', 'product__translations__title')
    list_filter = ('success',)
    raw_id_fields = ('product',)

    def get_queryset(self, request):
        queryset = super(XLSImportHistoryAdmin, self).get_queryset(request)
        queryset = queryset \
            .prefetch_related('product__translations')
        return queryset


admin.site.register(XLSImportHistory, XLSImportHistoryAdmin)
