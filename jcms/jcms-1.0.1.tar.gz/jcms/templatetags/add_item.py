from django import template

register = template.Library()


@register.simple_tag
def add_item(array, item):
    if not isinstance(array, (frozenset, list, set, tuple)):
        array = []

    array.append(item)
    return array
