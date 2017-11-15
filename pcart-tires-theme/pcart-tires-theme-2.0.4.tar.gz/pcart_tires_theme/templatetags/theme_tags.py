from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()


def get_url(url_name, *args, **kwargs):
    from django.urls import reverse, NoReverseMatch
    try:
        _link = reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return '#unknown-url'


@register.simple_tag
def get_collections(level=None):
    from pcart_catalog.models import Collection
    collections = Collection.objects.filter(published=True)
    if level is not None:
        collections = collections.filter(level=level)
    collections = collections.translated().prefetch_related('translations')
    return collections


@register.filter
def replace(value, arg):
    pair = arg.split(',')
    if len(pair) == 1:
        pair.append('')
    return value.replace(*pair)


@register.filter
def replace_alt(value, arg):
    pair = arg.split(':')
    if len(pair) == 1:
        pair.append('')
    return value.replace(*pair)


@register.filter
def asset_url(value):
    from django.contrib.staticfiles.templatetags.staticfiles import static
    chunks = value.split('?')
    result = static('assets/%s' % chunks[0])
    if len(chunks) > 1:
        result += '?%s' % chunks[1]
    return mark_safe(result)


@register.filter
def templated_asset_url(value):
    from django.urls import reverse
    return mark_safe(reverse('render_asset', args=[value]))


@register.filter
def stylesheet_tag(value):
    return mark_safe('<link href="%s" rel="stylesheet">' % value)


@register.filter
def script_tag(value):
    return mark_safe('<script src="%s" type="text/javascript"></script>' % value)


@register.filter
def shopify_asset_url(value):
    return mark_safe('<script src="//cdn.shopify.com/s/shopify/%s" type="text/javascript"></script>' % value)


@register.filter
def handle(value):
    from pcart_core.utils import slugify_unicode
    return slugify_unicode(value)


@register.filter
def img_tag(value, arg=''):
    _chunks = arg.split(',')
    _extra = ''
    if _chunks:
        _extra += ' alt="%s"' % _chunks[0]
        if len(_chunks) > 1:
            _extra += ' class="%s"' % _chunks[1]
    return '<img src="%s" %s>' % (value, _extra)


@register.filter
def link_to(label, url):
    return mark_safe('<a href="%s">%s</a>' % (url, label))


@register.filter
def customer_logout_link(label):
    return '<a href="%s">%s</a>' % (get_url('logout'), label)


@register.filter
def customer_register_link(label):
    return '<a href="%s">%s</a>' % (get_url('register'), label)


@register.filter
def customer_login_link(label):
    return '<a href="%s">%s</a>' % (get_url('login'), label)


@register.filter
def limit(sequence, limit):
    if sequence is None:
        return None
    else:
        return sequence[:limit]


@register.filter
def offset(sequence, offset):
    return sequence[offset:]


@register.filter(name='slice')
def _slice(sequence, arg):
    if type(arg) is int:
        return sequence[arg]
    elif type(arg) is str:
        _chunks = arg.split(',')
        return sequence[int(_chunks[0]):int(_chunks[0])+int(_chunks[1])]


@register.filter
def plus(value, arg):
    if value is None:
        return arg
    elif type(value) is str and type(arg) is int:
        return int(value) + arg
    elif type(value) is int and type(arg) is str:
        return value + int(arg)
    else:
        return value + arg


@register.filter
def minus(value, arg):
    if value is None:
        return arg
    elif type(value) is str and type(arg) is int:
        return int(value) - arg
    elif type(value) is int and type(arg) is str:
        return value - int(arg)
    else:
        return value - arg


@register.filter
def remove(value, arg):
    return value.replace(arg, '')


@register.filter
def divided_by(value, arg):
    if type(value) is str and type(arg) is int:
        return int(value) / arg
    elif type(value) is int and type(arg) is str:
        return value / int(arg)
    else:
        return value / arg


@register.filter
def modulo(value, arg):
    if type(value) is str and type(arg) is int:
        return int(value) % arg
    elif type(value) is int and type(arg) is str:
        return value % int(arg)
    else:
        return value % arg


@register.filter
def times(value, arg):
    if type(value) is str and type(arg) is int:
        return int(value) * arg
    elif type(value) is int and type(arg) is str:
        return value * int(arg)
    else:
        return value * arg


@register.filter(name='range')
def _range(value):
    chunks = value.split(',')
    if len(chunks) == 1:
        return range(int(chunks[0]))
    elif len(chunks) > 1:
        return range(int(chunks[0]), int(chunks[1]))


@register.filter(name='attr')
def _attr(obj, attr):
    return getattr(obj, attr)


@register.filter(name='element')
def _element(obj, element):
    if obj is None:
        return None
    elif obj == '':
        return ''
    else:
        return obj.get(element)


@register.filter(name='json')
def _json(value):
    import json
    return mark_safe(json.dumps(value))


@register.filter(name='split')
def _split(value, delimiter=','):
    return value.split(delimiter)


@register.filter(name='last')
def _last(sequence):
    return sequence[-1]


@register.filter(name='first')
def _first(sequence):
    return sequence[0]


@register.simple_tag(takes_context=True)
def get_template_name(context):
    return context.template.name
