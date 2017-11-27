from django import template

register = template.Library()


@register.filter
def crud_url(view_type, model):
    string = 'jcms:' + model.__class__.__name__.lower() + view_type
    return string
