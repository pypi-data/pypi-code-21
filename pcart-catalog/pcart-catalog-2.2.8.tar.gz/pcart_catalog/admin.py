from django.contrib import admin
from django.db import models
from mptt.admin import MPTTModelAdmin
from django.utils.translation import ugettext_lazy as _
from adminsortable.admin import NonSortableParentAdmin, SortableTabularInline, SortableAdmin
from django.utils.safestring import mark_safe
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from pcart_treeadmin.admin import TreeAdmin
from cms.admin.placeholderadmin import PlaceholderAdminMixin
from parler.admin import TranslatableAdmin, TranslatableTabularInline, TranslatableStackedInline
from .models import (
    Collection,
    ProductType,
    ProductTypeProperty,
    ProductStatus,
    Product,
    ProductVariant,
    ProductImage,
    Vendor,
    PropertyValueSlug,
    PriceAggregationProfile,
)
from .forms import (
    EditProductVariantForm,
    EditProductVariantFormSet,
    EditCollectionForm,
    EditProductImageForm,
    PriceAggregationProfileForm,
)
from .settings import PCART_ENABLE_PRODUCT_VARIANTS


class VendorAdmin(TranslatableAdmin):
    list_display = ('title', 'slug', 'has_image')
    search_fields = ['translations__title', 'slug', 'id']

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}

    def has_image(self, obj) -> bool:
        return bool(obj.image)
    has_image.short_description = _('Has image')
    has_image.boolean = True

    def get_queryset(self, request):
        qs = super(VendorAdmin, self).get_queryset(request)
        return qs.prefetch_related('translations').translated().order_by('translations__title')


admin.site.register(Vendor, VendorAdmin)


class CollectionAdmin(PlaceholderAdminMixin, TranslatableAdmin, TreeAdmin):
    form = EditCollectionForm
    list_display = ('title_preview', 'changed', 'published', 'virtual', 'badged', 'site', 'slug')
    list_filter = ('published', 'site')
    preserve_filters = True
    search_fields = ['translations__title', 'id']
    fieldsets = (
        (None, {
            'fields': ('site', 'title', 'slug', 'parent', 'description', 'image'),
        }),
        (_('SEO'), {
            'fields': ('page_title', 'meta_description', 'meta_keywords', 'meta_text'),
            'classes': ('collapse',),
        }),
        (_('Product selection'), {
            'fields': (
                'products_selection',
                'condition_vendors',
                'condition_product_types',
                'condition_min_price',
                'condition_max_price',
                'mandatory_tags',
                'optional_tags',
            ),
            'classes': ('collapse',),
        }),
        (_('Triggers'), {
            'fields': ('trigger_regex', 'trigger_module'),
            'classes': ('collapse',),
        }),
        (_('Filters'), {
            'fields': (
                'custom_url_filter_rules',
                'url_filter_rules',
                'show_vendor_filter', 'show_properties_filters', 'exclude_properties_filters',
                'show_price_filter',
            ),
            'classes': ('collapse',),
        }),
        (_('Publication'), {
            'fields': ('published', 'virtual', 'badged'),
        }),
    )
    filter_horizontal = ('condition_vendors', 'condition_product_types')

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}

    def title_preview(self, obj):
        return mark_safe('%s%s' % ('&nbsp;'*obj.level*4, obj.title))
    title_preview.short_description = _('Title')
    # title_preview.admin_order_field = 'title'

    def get_queryset(self, request):
        qs = super(CollectionAdmin, self).get_queryset(request)
        return qs.prefetch_related('translations').translated()


admin.site.register(Collection, CollectionAdmin)


class ProductTypePropertyAdmin(SortableAdmin):
    list_display = (
        'title', 'product_type', 'default_value',
        'tag_prefix', 'use_in_filters', 'for_variants', 'hidden',
    )
    search_fields = ('title',)
    list_filter = ('product_type',)


admin.site.register(ProductTypeProperty, ProductTypePropertyAdmin)

# class ProductTypePropertyInline(SortableTabularInline):
#     model = ProductTypeProperty
#     exclude = tuple() if PCART_ENABLE_PRODUCT_VARIANTS else ('for_variants',)
#     extra = 1


class ProductTypeAdmin(PlaceholderAdminMixin, TranslatableAdmin):  # , NonSortableParentAdmin
    list_display = ('title', 'id')
    search_fields = ['translations__title']
    # inlines = [ProductTypePropertyInline]
    fieldsets = (
        (None, {
            'fields': ('title',),
        }),
        (_('SEO'), {
            'fields': ('page_title', 'meta_description', 'meta_keywords', 'meta_text'),
            'classes': ('collapse',),
        }),
        (_('Details'), {
            'fields': ('default_quantity_for_purchase',),
            'classes': ('collapse',),
        })
    )

    def get_queryset(self, request):
        qs = super(ProductTypeAdmin, self).get_queryset(request)
        return qs.prefetch_related('translations').translated()


admin.site.register(ProductType, ProductTypeAdmin)


class ProductStatusAdmin(TranslatableAdmin):
    list_display = ('title', 'show_buy_button', 'is_visible', 'is_searchable', 'weight')
    search_fields = ['translations__title']
    fieldsets = (
        (None, {
            'fields': ('title',),
        }),
        (_('Features'), {
            'fields': (
                'show_buy_button', 'is_visible', 'is_searchable',
            )
        }),
        (_('Priority'), {
            'fields': ('weight',),
        }),
    )

    def get_queryset(self, request):
        qs = super(ProductStatusAdmin, self).get_queryset(request)
        return qs.prefetch_related('translations').translated()


admin.site.register(ProductStatus, ProductStatusAdmin)


class ProductImageInline(SortableTabularInline, TranslatableTabularInline):
    model = ProductImage
    extra = 1
    form = EditProductImageForm


class ProductVariantInline(TranslatableTabularInline):
    model = ProductVariant
    readonly_fields = ['tags']
    form = EditProductVariantForm
    formset = EditProductVariantFormSet
    extra = 1

    def get_fields(self, request, obj=None):
        exclude_prop_fields = tuple(p[0] for p in obj.get_properties_fields(for_variants=True))
        self.exclude = exclude_prop_fields
        fields = ('title', 'slug', 'tags', 'sku', 'barcode', 'status', 'price', 'compare_at_price', 'price_varies') + exclude_prop_fields
        return fields


class ProductAdmin(FrontendEditableAdminMixin, TranslatableAdmin, NonSortableParentAdmin):
    list_display = (
        'show_title',
        # 'vendor',
        'status',
        'show_price',
        'product_type',
        'get_collections',
        'published')
    list_filter = ('published', 'status', 'product_type')
    filter_horizontal = ('collections',)
    preserve_filters = True
    search_fields = ['translations__title', 'id']
    inlines = [ProductImageInline, ProductVariantInline]
    save_as_continue = True

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}

    def get_queryset(self, request):
        queryset = super(ProductAdmin, self).get_queryset(request)
        queryset = queryset \
            .prefetch_related('translations') \
            .prefetch_related('vendor')\
            .prefetch_related('vendor__translations')\
            .prefetch_related('status')\
            .prefetch_related('status__translations')\
            .prefetch_related('product_type')\
            .prefetch_related('product_type__translations')\
            .prefetch_related('collections')\
            .prefetch_related('collections__translations')
        return queryset

    def show_price(self, obj):
        if obj.variants_count > 0:
            return '%s - %s' % (obj.min_variant_price, obj.max_variant_price)
        else:
            if obj.compare_at_price != 0:
                return '%s --%s--' % (obj.price, obj.compare_at_price)
            else:
                return '%s' % obj.price
    show_price.short_description = _('Price')
    show_price.admin_order_field = 'min_variant_price'

    def get_collections(self, obj):
        return ', '.join([x.title for x in obj.collections.all()])
    get_collections.short_description = _('Collections')

    def show_title(self, obj):
        from django.utils.html import format_html
        if obj.variants_count > 0:
            return format_html(
                '{0} <span style="float:right;"><strong>({1})</strong></span>',
                obj.title,
                obj.variants_count)
        else:
            return obj.title
    show_title.short_description = _('Title')
    # show_title.admin_order_field = 'title'

    def get_form(self, request, obj=None, **kwargs):
        from .forms import AddProductForm, EditProductForm
        if obj is None:
            kwargs['form'] = AddProductForm
        else:
            kwargs['form'] = EditProductForm
        return super(ProductAdmin, self).get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            self.exclude = []
            return (
                (None, {
                    'fields': ('title', 'slug', 'product_type', 'vendor', 'status'),
                }),
            )
        else:
            exclude_prop_fields = tuple(p[0] for p in obj.get_properties_fields())
            self.exclude = exclude_prop_fields
            return (
                (None, {
                    'fields': (
                        'title', 'slug', 'external_id', 'product_type', 'vendor', 'description'),
                }),
                (_('SEO'), {
                    'fields': ('page_title', 'meta_description', 'meta_keywords', 'meta_text'),
                    'classes': ('collapse',),
                }),
                (_('Tags'), {
                    'fields': ('tags', 'sku', 'barcode', 'status', 'quantity'),
                }),
                (_('Properties'), {
                    'fields': exclude_prop_fields,
                }),
                (_('Price'), {
                    'fields': ('price', 'compare_at_price', 'price_varies', 'max_variant_price', 'min_variant_price'),
                }),
                (_('Shipping'), {
                    'fields': ('weight',),
                    'classes': ('collapse',),
                }),
                (_('Additional data'), {
                    'fields': (
                        'rank_1', 'rank_2', 'rank_3',
                        'extra_int_1', 'extra_int_2',
                        'extra_float_1', 'extra_float_2',
                        'extra_price_1', 'extra_price_2', 'extra_price_3',
                        'extra_text_1', 'extra_text_2',
                        'extra_data',
                        'extra_id_1', 'extra_id_2',
                    ),
                    'classes': ('collapse',),
                }),
                (_('Publication'), {
                    'fields': ('collections', 'published', 'variants_count', 'added', 'changed'),
                }),
            )

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide ProductVariantInline in the add view
            if isinstance(inline, ProductVariantInline) and obj is None:
                continue
            elif isinstance(inline, ProductVariantInline) and PCART_ENABLE_PRODUCT_VARIANTS is False:
                continue
            yield inline.get_formset(request, obj), inline

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        else:
            if obj.variants_count == 0:
                return (
                    'product_type',
                    'tags',
                    'min_variant_price',
                    'max_variant_price',
                    'variants_count',
                    'added',
                    'changed',
                )
            else:
                return (
                    'product_type',
                    'tags',
                    'status',
                    'min_variant_price',
                    'max_variant_price',
                    'variants_count',
                    'added',
                    'changed',
                )


admin.site.register(Product, ProductAdmin)


class PropertyValueSlugAdmin(admin.ModelAdmin):
    list_display = ('value', 'slug')
    search_fields = ('value', 'slug')


admin.site.register(PropertyValueSlug, PropertyValueSlugAdmin)


class PriceAggregationProfileAdmin(admin.ModelAdmin):
    list_display = ('title', 'site', 'language', 'file_name', 'template_name')
    search_fields = ('title',)
    form = PriceAggregationProfileForm
    actions = ['generate_file']

    def generate_file(self, request, queryset):
        from .tasks import generate_price_aggregation_file
        for q in queryset:
            generate_price_aggregation_file.delay(q.pk)
    generate_file.short_description = _('Generate aggregation file')


admin.site.register(PriceAggregationProfile, PriceAggregationProfileAdmin)
