from django import template

register = template.Library()


@register.filter
def add_str(value, arg):
    """
    Same as :py:func:`django.template.defaultfilters.add` but always convert to ``str``.
    """
    return str(value) + str(arg)
