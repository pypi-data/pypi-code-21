from django import template

register = template.Library()


@register.filter
def get_object_attr(use_object, name):
    return getattr(use_object, name)
