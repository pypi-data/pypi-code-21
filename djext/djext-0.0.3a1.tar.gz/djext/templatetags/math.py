from django import template

register = template.Library()


@register.simple_tag(name='mult')
def multiply(x, y):
    return int(x) * int(y)


@register.simple_tag(name='sub')
def subtract(x, y):
    return int(x) - int(y)


@register.simple_tag(name='div')
def divide(x, y):
    return int(x) / int(y)


