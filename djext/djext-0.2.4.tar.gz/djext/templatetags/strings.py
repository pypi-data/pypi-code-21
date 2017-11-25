from django import template

register = template.Library()


@register.filter(name='concat')
def concat(arg1, arg2):
    return str(arg1) + str(arg2)
