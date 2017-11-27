from django import template

register = template.Library()


@register.filter
def get_model_name(model):
    return model.__class__.__name__
