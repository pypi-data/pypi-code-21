from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Cart, OrderNumberFormat, Order, OrderStatus


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'site', 'added', 'changed')
    raw_id_fields = ('customer',)
    search_fields = ['id', 'customer']
    date_hierarchy = 'changed'
    readonly_fields = ['content_preview']
    fields = ['site', 'customer', 'content_preview', 'note']

    def content_preview(self, obj):
        from django.template.loader import render_to_string
        context = {
            'cart': obj,
        }
        return render_to_string('admin/cart/cart_preview.html', context)
    content_preview.allow_tags = True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        result = super(CartAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

        if object_id and request.method == 'POST':
            try:
                cart = Cart.objects.get(pk=object_id)
                for k in request.POST:
                    if k.startswith('item-quantity-'):
                        _id = k[len('item-quantity-'):]
                        cart.change_item_quantity(_id, request.POST.get(k, 0))
                    elif k.startswith('item-remove-'):
                        _id = k[len('item-remove-'):]
                        cart.remove_item(_id)
            except Cart.DoesNotExist:
                pass

        return result


admin.site.register(Cart, CartAdmin)


class OrderNumberFormatAdmin(admin.ModelAdmin):
    list_display = ('site', 'template', 'last_number', 'example')

    def example(self, obj):
        return obj.template % obj.last_number
    example.short_description = _('Example')

admin.site.register(OrderNumberFormat, OrderNumberFormatAdmin)


class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'weight')
    search_fields = ('title', 'slug')


admin.site.register(OrderStatus, OrderStatusAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer', 'site', 'total_price', 'added', 'status', 'changed', 'export_status')
    search_fields = ('customer', 'number')
    date_hierarchy = 'added'
    raw_id_fields = ('customer',)
    readonly_fields = (
        'number', 'content_preview', 'total_price', 'total_weight',
        'shipping_preview', 'payment_preview')
    ordering = ('-added',)
    fields = [
        'site', 'customer', 'status', 'export_status', 'content_preview',
        'shipping_preview',
        'shipping_data',
        'payment_preview',
        'payment_data',
        'total_price', 'total_weight', 'note',
    ]

    def content_preview(self, obj):
        from django.template.loader import render_to_string
        context = {
            'order': obj,
        }
        return render_to_string('admin/cart/order_preview.html', context)
    content_preview.allow_tags = True

    def shipping_preview(self, obj):
        return obj.get_shipping_info()
    shipping_preview.allow_tags = True

    def payment_preview(self, obj):
        return obj.get_payment_info()
    payment_preview.allow_tags = True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        result = super(OrderAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

        if object_id and request.method == 'POST':
            try:
                order = Order.objects.get(pk=object_id)
                for k in request.POST:
                    if k.startswith('item-quantity-'):
                        _id = k[len('item-quantity-'):]
                        order.change_item_quantity(_id, request.POST.get(k, 0))
                    elif k.startswith('item-remove-'):
                        _id = k[len('item-remove-'):]
                        order.remove_item(_id)
            except Order.DoesNotExist:
                pass
        return result


admin.site.register(Order, OrderAdmin)
