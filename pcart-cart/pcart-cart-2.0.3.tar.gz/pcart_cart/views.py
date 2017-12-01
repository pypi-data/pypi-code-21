from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, Http404
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from pcart_customers.utils import get_customer
from .utils import get_or_create_cart, create_order
from .forms import OrderCheckoutForm


def cart_page_view(request, template_name='cart/cart.html'):
    customer = get_customer(request)
    site = get_current_site(request)
    cart = get_or_create_cart(site, customer)

    if 'view' in request.GET:
        template_name = settings.PCART_CART_TEMPLATES[request.GET['view']]

    _update_cart = False
    if request.method == 'POST':
        if 'update' in request.POST or 'checkout' in request.POST:
            if 'note' in request.POST:
                cart.note = request.POST['note']
                _update_cart = True
            for k in request.POST:
                if k.startswith('item-quantity-'):
                    _id = k[len('item-quantity-'):]
                    cart.change_item_quantity(_id, request.POST.get(k, 0))
            if 'checkout' in request.POST:
                return redirect(reverse('pcart_cart:checkout'))
        else:
            for k in request.POST:
                if k.startswith('item-remove-'):
                    _id = k[len('item-remove-'):]
                    cart.remove_item(_id)

    if _update_cart:
        cart.save()
    context = {
        'customer': customer,
        'cart': cart,
    }

    if request.is_ajax() and request.GET.get('ignore-response', 'no') == 'yes':
        return HttpResponse('OK')

    return render(request, template_name, context)


@csrf_exempt
@require_http_methods(['POST'])
def add_to_cart(request):
    customer = get_customer(request)
    site = get_current_site(request)
    cart = get_or_create_cart(site, customer)
    if 'item-id' in request.POST:
        cart.add_item(
            item_id=request.POST['item-id'],
            item_type=request.POST.get('item-type', 'product'),
            price=request.POST.get('price', 0.00),
            quantity=request.POST.get('quantity', 1),
            weight=request.POST.get('weight', 0),
        )

    if not request.is_ajax() and 'next' in request.POST:
        return redirect(request.POST['next'])
    return HttpResponse('OK')


def checkout(request, template_name='cart/checkout.html'):
    from .utils import get_shipping_method
    customer = get_customer(request)
    site = get_current_site(request)
    cart = get_or_create_cart(site, customer)

    if 'print' in request.GET:
        template_name = 'cart/print_checkout.html'

    if request.method == 'POST':
        checkout_form = OrderCheckoutForm(request.POST, customer=customer)

        if 'checkout' in request.POST:
            if checkout_form.is_valid():
                shipping_method = get_shipping_method(checkout_form.cleaned_data['shipping_method'])
                shipping_form = shipping_method.get_form(request, request.POST)
                shipping_data = None
                if shipping_form is not None and shipping_form.is_valid():
                    shipping_data = shipping_form.cleaned_data

                order = create_order(
                    cart,
                    name=checkout_form.cleaned_data['name'],
                    email=checkout_form.cleaned_data['email'],
                    phone=checkout_form.cleaned_data['phone'],
                    shipping_method=checkout_form.cleaned_data['shipping_method'],
                    payment_method=checkout_form.cleaned_data['payment_method'],
                    note=checkout_form.cleaned_data['note'],
                    shipping_data=shipping_data,
                )
                if order:
                    return redirect(reverse('pcart_cart:thanks', args=[order.number]))
    else:
        checkout_form = OrderCheckoutForm(initial={
            'name': customer.name,
            'email': request.user.email if request.user.is_authenticated() else '',
            'phone': request.user.phone if request.user.is_authenticated() else '',
            'note': cart.note,
            'shipping_method': 'office',
        }, customer=customer)

    context = {
        'customer': customer,
        'cart': cart,
        'checkout_form': checkout_form,
    }
    return render(request, template_name, context)


def thanks(request, order_number, template_name='cart/thanks.html'):
    from .models import Order
    customer = get_customer(request, create=False)
    if customer.user is not None:
        customer.session_id = ''
        customer.save()
    try:
        order = Order.objects.get(number=order_number)
        if order.customer != customer:
            return HttpResponseForbidden('Access denied.')

        context = {
            'order': order,
        }
        return render(request, template_name, context)
    except Order.DoesNotExist:
        raise Http404


def my_orders(request, template_name='cart/my_orders.html'):
    from .models import Order
    customer = get_customer(request)
    site = get_current_site(request)

    orders = Order.objects.filter(customer=customer, site=site).order_by('-added')
    context = {
        'orders': orders,
        'customer_menu': settings.PCART_CUSTOMER_PROFILE_SECTIONS,
    }
    return render(request, template_name, context)


def shipping_form(request, slug=None):
    from .utils import get_shipping_method
    if not request.is_ajax():
        return HttpResponseForbidden('Ajax request required')
    shipping_method = get_shipping_method(slug)
    if shipping_method is None:
        return HttpResponseNotFound('Shipping method not found')

    is_valid = False
    if request.method == 'POST':
        form = shipping_method.get_form(request, request.POST)
        if form.is_valid():
            is_valid = True
    else:
        form = shipping_method.get_form(request)
    context = {
        'shipping_method': shipping_method,
        'form': form,
        'is_valid': is_valid,
    }
    return render(request, shipping_method.get_form_template(request), context)

