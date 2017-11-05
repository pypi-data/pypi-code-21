from ckeditor_uploader.widgets import CKEditorUploadingWidget
from decimal import Decimal
from django.contrib import admin
from django.db import transaction
from django.db import models
from django.db.models import Q, Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import ProductCategory, Product, ProductImage, ProductEntry, \
    DeliveryType, PaymentType, Order, ProductOrder, \
    ProductCategoryCustomField, ProductCustomFieldValue, PackagingBox, CustomersCart, ProductInCart
from .admin_forms import ProductImageAdminForm, DeliveryTypeAdminForm, \
    PaymentTypeAdminForm, ProductCategoryCustomFieldForm, \
    ProductCustomFieldValueForm
from .utils.payment import get_description
from .utils.delivery import get_description as get_delivery_description


class ProductCategoryCustomFieldInline(admin.StackedInline):
    form = ProductCategoryCustomFieldForm
    model = ProductCategoryCustomField
    extra = 0
    fields = (
        ('name', 'key'),
        ('type', 'choices'),
        ('is_filter', 'required', 'hidden'),
    )
    prepopulated_fields = {
        'key': ('name',),
    }


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    form = ProductImageAdminForm
    list_display = ('name', 'priority')
    prepopulated_fields = {
        'slug': ('name',),
    }
    list_filter = ('type', 'is_hidden')
    fields = (
        ('name', 'priority'),
        'slug',
        'parent',
        'type',
        'is_hidden',
        'description',
        'image'
    )

    formfield_overrides = {
        models.TextField: {'widget': CKEditorUploadingWidget},
    }

    inlines = [
        ProductCategoryCustomFieldInline
    ]

    def get_fields(self, request, obj=None):
        if not request.user.has_perm('django_shop.category_can_edit_important'):
            return ProductCategory.NON_IMPORTANT_FIELDS
        return super(ProductCategoryAdmin, self).get_fields(request, obj=obj)

    def get_prepopulated_fields(self, request, obj=None):
        if not request.user.has_perm('django_shop.category_can_edit_important'):
            return {}
        return super(ProductCategoryAdmin, self).get_prepopulated_fields(request, obj=obj)

    def save_related(self, request, form, formsets, change):
        super(ProductCategoryAdmin, self).save_related(request, form,
                                                       formsets, change)
        for p in form.instance.products.all():
            p.check_fields()


class ProductImageInline(admin.TabularInline):
    form = ProductImageAdminForm
    model = ProductImage
    extra = 1


class ProductEntryInline(admin.TabularInline):
    fields = ('quantity', 'price')
    model = ProductEntry
    extra = 1

    def get_queryset(self, request):
        qs = super(ProductEntryInline, self).get_queryset(request)
        return qs.filter(quantity__gt=0)


class ProductCustomValueInline(admin.TabularInline):
    model = ProductCustomFieldValue
    form = ProductCustomFieldValueForm
    fields = ('field', 'value')
    readonly_fields = ('field',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class InStockListFilter(admin.SimpleListFilter):
    title = 'Наличие'
    parameter_name = 'in_stock'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'В наличии'),
            ('no', 'Нет в наличии'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(
                Q(is_unlimited=True) | Q(entries__quantity__gt=0)
            )
        if self.value() == 'no':
            return queryset.annotate(
                in_stock=Coalesce(Sum('entries__quantity'), Value(0))).filter(
                    Q(is_unlimited=False) & Q(in_stock=0)
                )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'in_stock', 'is_weight')
    prepopulated_fields = {
        'slug': ('name',),
    }
    inlines = [
        ProductImageInline,
        ProductEntryInline,
    ]
    filter_horizontal = ('categories',)
    list_filter = (
        ('categories', admin.RelatedOnlyFieldListFilter),
        InStockListFilter,
    )
    actions = ['copy_products']

    formfield_overrides = {
        models.TextField: {'widget': CKEditorUploadingWidget},
    }

    def get_fields(self, request, obj=None):
        if not request.user.has_perm('django_shop.category_can_edit_important'):
            return Product.NON_IMPORTANT_FIELDS
        return super(ProductAdmin, self).get_fields(request, obj=obj)

    def get_prepopulated_fields(self, request, obj=None):
        if not request.user.has_perm('django_shop.category_can_edit_important'):
            return {}
        return super(ProductAdmin, self).get_prepopulated_fields(request, obj=obj)

    def get_form(self, request, obj=None, **kwargs):
        if obj is not None and ProductCustomValueInline not in self.inlines:
            self.inlines = [ProductCustomValueInline] + self.inlines

        return super(ProductAdmin, self).get_form(request, obj=obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save()
        obj.check_fields()

    def save_related(self, request, form, formsets, change):
        super(ProductAdmin, self).save_related(request, form, formsets, change)
        form.instance.check_fields()

    def copy_products(self, request, queryset):
        if not request.user.has_perm('django_shop.add_product'):
            return
        for product in queryset:
            product.create_copy()
    copy_products.short_description = "Создать копии выбранных продуктов"


@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'payment_type', 'payment_hook_name', 'is_active')
    form = PaymentTypeAdminForm

    def payment_hook_name(self, obj):
        return get_description(obj.payment_hook)
    payment_hook_name.short_description = 'Конкретный тип онлайн оплаты'


@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    list_filter = ('is_autogenerated', 'city')
    list_display = ('name', 'pricing_method', 'delivery_hook',
                    'actual_pricing', 'is_active', 'is_autogenerated')
    form = DeliveryTypeAdminForm

    def delivery_hook_name(self, obj):
        return get_delivery_description(obj.delivery_hook)
    delivery_hook_name.short_description = 'Конкретный тип API доставки'


class ProductOrderInline(admin.TabularInline):
    fields = ('product_link', 'quantity', 'stock_price', 'price')
    readonly_fields = ('product_link', 'quantity', 'stock_price', 'price')
    model = ProductOrder
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def product_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(reverse('admin:django_shop_product_change',
                                                              args=(obj.product.id,)), obj))
    product_link.short_description = "Продукт"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_filter = ('state',)
    list_display = ('id', 'products_string_html', 'customer_name', 'state', 'created',
                    'changed', 'full_price')
    fields = ('state', 'created', 'changed', 'delivery_type', 'delivery_price',
              'receiver_html', 'full_price', 'payment_method')
    readonly_fields = ('created', 'changed', 'receiver_html', 'full_price',
                       'payment_method')
    search_fields = ('delivery_address__email', 'delivery_address__phone')
    inlines = [
        ProductOrderInline
    ]

    def get_actions(self, request):
        actions = super(OrderAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def get_form(self, request, obj=None, **kwargs):
        form = super(OrderAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            # Modify form.base_fields['state'].choices
            form.base_fields['state'].choices = obj.get_state_choices()
        return form

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            if change:
                current_version = Order.objects.get(pk=obj.id)
                if current_version.state == Order.STATE_CREATED and \
                        obj.state == Order.STATE_CONFIRMED:
                    obj.reduce_stock_amount()

            obj.save()

    def products_string_html(self, obj):
        return mark_safe(obj.products_string.replace('\n', '<br>'))
    products_string_html.short_description = 'Заказ'

    def customer_name(self, obj):
        return mark_safe('<br>'.join(map(str, filter(None, (
            obj.delivery_address.name,
            obj.delivery_address.email,
            obj.delivery_address.phone,
        )))))
    customer_name.short_description = 'Заказчик'


class ProductInCartAdminInline(admin.TabularInline):
    fields = ('product', 'quantity', 'product_link', 'price', 'total_price')
    readonly_fields = ('product_link', 'price', 'total_price')
    model = ProductInCart
    extra = 0

    def product_link(self, obj):
        return mark_safe('<a href="{}">Ссылка</a>'.format(reverse('admin:django_shop_product_change',
                                                                  args=(obj.product.id,))))
    product_link.short_description = "Ссылка на продукт"

    def price(self, obj):
        return obj.product.price
    price.short_description = "Цена за единицу"

    def total_price(self, obj):
        return obj.product.price * obj.quantity
    total_price.short_description = "Цена за весь товар"


@admin.register(CustomersCart)
class CustomersCartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'total', 'actions_num', 'items_num', 'has_order', 'created', 'updated')
    readonly_fields = ('customer', 'total', 'delivery_type', 'payment_method', 'name',
                       'phone', 'email', 'order_link', 'created', 'updated', 'actions_log', 'known_info')
    fields = ('customer', 'total', 'order_link',
              ('delivery_type', 'payment_method'),
              ('name', 'phone', 'email'),
              ('created', 'updated'),
              'actions_log',
              'known_info')
    inlines = [
        ProductInCartAdminInline
    ]

    def get_queryset(self, request):
        qs = super(CustomersCartAdmin, self).get_queryset(request)
        return qs.select_related('customer').prefetch_related('products', 'products__product')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_order(self, obj):
        return obj.order is not None
    has_order.short_description = 'Сделан заказ'
    has_order.boolean = True

    def actions_num(self, obj):
        return len(obj.logs.all())
    actions_num.short_description = 'Количество действий'

    def items_num(self, obj):
        return len(obj.products.all())
    items_num.short_description = 'Количество товаров'

    def order_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(reverse('admin:django_shop_order_change',
                                                              args=(obj.order.id,)), obj.order))
    order_link.short_description = 'Заказ'

    def total(self, obj):
        res = Decimal(0)
        for pic in obj.products.all():
            res += pic.product.price * pic.quantity
        return res
    total.short_description = 'На сумму'

    def actions_log(self, obj):
        result = ''
        for entry in obj.logs.all():
            result += '<b>{}</b>: {}<br>'.format(entry.log_date.strftime('%Y-%m-%d %H:%M'), entry.message)
        return mark_safe(result)
    actions_log.short_description = 'Действия'

    def known_info(self, obj):
        result = ''
        for entry in obj.customer.fields.order_by('-type'):
            result += '<b>{}</b>: {}<br>'.format(entry.get_type_display(), entry.value)
        return mark_safe(result)
    known_info.short_description = 'Известная информация'


admin.site.register(PackagingBox)
