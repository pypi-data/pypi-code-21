from django.utils.module_loading import import_string
from django.conf import settings


def get_or_create_cart(site, customer):
    from .models import Cart
    try:
        cart = Cart.objects.get(site=site, customer=customer)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(site=site, customer=customer)
    return cart


def next_order_number(site):
    from .models import OrderNumberFormat
    number_format = OrderNumberFormat.objects.get(site=site)
    return str(number_format)


def increase_order_number(site):
    from .models import OrderNumberFormat
    number_format = OrderNumberFormat.objects.get(site=site)
    number_format.increase_number()
    return str(number_format)


def create_order(
        cart, name=None, email=None, phone=None, shipping_method=None, payment_method=None, note=None,
        shipping_data=None, payment_data=None):
    from .models import Order
    site = cart.site
    order_number = next_order_number(site)

    if shipping_method:
        shipping_data = {
            'method': shipping_method,
            'data': shipping_data,
        }
    else:
        shipping_data = dict()
    if payment_method:
        payment_data = {
            'method': payment_method,
            'data': payment_data,
        }
    else:
        payment_data = dict()

    order = Order(
        site=site,
        number=order_number,
        customer=cart.customer,
        content=cart.content,
        note=note or cart.note,
        shipping_data=shipping_data,
        payment_data=payment_data,
    )
    order.save()
    increase_order_number(site)
    cart.clear()

    _customer = cart.customer
    if _customer.user is None:
        # Register new user
        from pcart_customers.utils import create_user_for_customer
        _customer.name = name or ''
        _customer.save()
        create_user_for_customer(_customer, email, phone)
    else:
        if _customer.name == '' and name is not None:
            _customer.name = name
            _customer.save()

    order.send_message()
    return order


def get_shipping_method(name):
    for m in settings.PCART_SHIPPING_METHODS:
        if m['name'] == name or name is None:
            _shipping_method_class = import_string(m['backend'])
            return _shipping_method_class(config=m.get('config', {}))


def get_payment_method(name):
    for m in settings.PCART_PAYMENT_METHODS:
        if m['name'] == name or name is None:
            _payment_method_class = import_string(m['backend'])
            return _payment_method_class(config=m.get('config', {}))

