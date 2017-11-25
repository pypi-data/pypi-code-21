from django import template
from django.template import Variable, VariableDoesNotExist

register = template.Library()


@register.assignment_tag(name='eq')
def equal(item1, item2):
    return item1 == item2


def resolve_base(target, lookup, default=None):
    try:
        return Variable(lookup).resolve(target)
    except VariableDoesNotExist:
        return default


@register.simple_tag(name='resolve')
def resolve(target, lookup, default=None):
    return resolve_base(target, lookup, default)


@register.assignment_tag(name='resolve_as')
def resolve_as(target, lookup, default=None):
    return resolve_base(target, lookup, default)
