from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_cart_amount(context, product):
    cart = context['cart']
    return cart.get_amount(product)


@register.filter
def add_media(value):
    if isinstance(value, str):
        if not value.startswith('/media/'):
            return '/media/{}'.format(value)
        return value
    else:
        return value.url
