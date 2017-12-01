from django.urls import reverse, NoReverseMatch
from django import template
register = template.Library()


@register.filter
def filter_for_tags(queryset, filter_tags):
    return queryset.filter(tags__contains=filter_tags)


@register.filter
def published(queryset):
    return queryset.filter(published=True)


@register.simple_tag
def add_to_cart_url():
    try:
        return reverse('pcart_cart:add-to-cart')
    except NoReverseMatch:
        return '#no-page-for-cart'
