from django import template

register = template.Library()


@register.simple_tag
def assign(the_object):
    return the_object
