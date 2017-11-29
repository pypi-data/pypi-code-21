from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()

# Debugging

@register.simple_tag
def debug_print(*values):
    if settings.DEBUG:
        print(*values)
        return values
    else:
        return ''


@register.simple_tag(takes_context=True)
def debug_context(context):
    if settings.DEBUG:
        print(context)
        return context
    else:
        return ''


# Helpful tags and filters

@register.filter
def is_subset(sequence_1, sequence_2):
    return set(sequence_1).issubset(sequence_2)


@register.filter
def is_superset(sequence_1, sequence_2):
    return set(sequence_1).issuperset(sequence_2)


@register.simple_tag
def random():
    import random
    return random.random()


@register.simple_tag
def randint(a, b):
    import random
    return random.randint(a, b)


@register.simple_tag
def timezone_now():
    from django.utils import timezone
    return timezone.now()


@register.filter
def get_element(iterable, index):
    return iterable.get(index)


@register.filter
def index_element(iterable, index):
    return iterable[index]


@register.filter
def to_list(obj):
    return list(obj)


@register.filter
def to_set(obj):
    return set(obj)


@register.filter
def to_dict(obj):
    return dict(obj)


@register.filter
def to_int(obj):
    return int(obj)


@register.filter
def to_float(obj):
    return float(obj)


@register.filter
def to_decimal(obj):
    from decimal import Decimal
    return Decimal(obj)


@register.filter
def ignore_none(value):
    return value or ''


@register.filter
def sort(iterable):
    return iterable.sort()


@register.filter
def sort_by_attr(iterable, attr):
    result = sorted(iterable, key=lambda x: getattr(x, attr))
    return result


@register.filter
def sort_by_key(iterable, key):
    result = sorted(iterable, key=lambda x: x[key])
    return result


@register.filter
def widget_css_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


@register.filter
def widget_placeholder(field, value):
    return field.as_widget(attrs={"placeholder": value})


@register.simple_tag
def widget_attrs(field, **kwargs):
    return field.as_widget(attrs=kwargs)


@register.filter
def markdown(text):
    import markdown
    return mark_safe(markdown.markdown(text))


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def add(value, arg):
    return value + arg


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def divide(value, arg):
    return value / arg


@register.filter
def append_to_list(value, arg):
    return value.append(arg)


@register.simple_tag(takes_context=True)
def theme_url(context, filename):
    from ..utils import get_settings_upload_url
    return get_settings_upload_url(context['site'].id, filename)


@register.simple_tag
def optional_url(url_name, *args, **kwargs):
    from django.urls import reverse, NoReverseMatch
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return '#unknown-url'


@register.filter
def is_checkbox(field):
    from django.forms import CheckboxInput
    return isinstance(field.field.widget, CheckboxInput)


@register.filter
def is_hidden_input(field):
    from django.forms import HiddenInput
    return isinstance(field.field.widget, HiddenInput)


@register.filter
def weight(value):
    return '%.1f kg' % value


@register.simple_tag(takes_context=True)
def render_string(context, template_string, **kwargs):
    """
    Renders `template_string` content as a Django template with given context.
    """
    from django.template import Context, Template
    _header = '{% load i18n l10n pcart_core staticfiles %}'
    _template = _header + template_string

    t = Template(_template)
    _context = context
    _context.update(kwargs)
    c = Context(_context)
    return mark_safe(t.render(c))


@register.simple_tag
def call_method(obj, method, *args, **kwargs):
    m = getattr(obj, method)
    return m(*args, **kwargs)


@register.simple_tag
def create_list(*args):
    return args


@register.simple_tag
def create_dict(**kwargs):
    return kwargs


@register.simple_tag
def save(value):
    return value


@register.simple_tag
def create_list():
    return list()


@register.simple_tag
def create_dict():
    return dict()


@register.filter
def attrs_list(obj):
    return dir(obj)


@register.filter
def inspect(obj):
    attrs = dir(obj)
    result = dict()
    for attr in attrs:
        result[attr] = getattr(obj, attr)
    return result


@register.simple_tag
def split_str(value, delimiter=','):
    return value.split(delimiter)


@register.simple_tag
def group_sequence_by_attr(sequence, attr_name):
    from collections import OrderedDict
    result = OrderedDict()
    for item in sequence:
        if isinstance(item, dict):
            result[item.get(attr_name)] = item
        else:
            result[getattr(item, attr_name)] = item
    return result


@register.filter
def money(value, template_name='price_template'):
    if value is None or value == '':
        value = 0.0

    _template = '<span class="money" data-value="%s" data-currency="%s">%s</span>'
    currency_code = getattr(settings, 'PCART_DEFAULT_CURRENCY', 'default')

    if hasattr(settings, 'PCART_CURRENCIES'):
        currency_config = settings.PCART_CURRENCIES.get(currency_code)
        return mark_safe(
            _template % (
                value,
                currency_code,
                currency_config.get(template_name, '%s') % value)
            )
    else:
        return _template % (value, currency_code, value)


@register.simple_tag
def set_query_parameter(url, param_name, param_value):
    from urllib.parse import (
        urlencode,
        parse_qs,
        urlsplit,
        urlunsplit,
    )
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


@register.simple_tag(takes_context=True)
def build_absolute_uri(context, location):
    return context['request'].build_absolute_uri(location)


@register.filter(name='len')
def _len(sequence):
    return len(sequence)


# Querysets

@register.filter
def order_by(queryset, values):
    values_attrs = values.split(',')
    return queryset.order_by(*values_attrs)


@register.filter
def select_related(queryset, value):
    return queryset.select_related(value)


@register.filter
def prefetch_related(queryset, value):
    return queryset.prefetch_related(value)


@register.filter
def distinct(queryset):
    return queryset.distinct()


@register.simple_tag
def prepare_query_object(logic='AND', **kwargs):
    from django.db.models import Q
    query = None
    for k,v in kwargs.items():
        if query is None:
            query = Q(**{k: v})
        else:
            if logic == 'AND':
                query &= Q(**{k: v})
            elif logic == 'OR':
                query |= Q(**{k: v})
    return query


@register.filter
def filter_queryset(queryset, query):
    return queryset.filter(query)


@register.filter
def exclude_from_queryset(queryset, query):
    return queryset.exclude(query)

# Liquid compatibility


@register.filter
def append(value, arg):
    """Appends characters to a string.
    Input:
        {{ 'sales' | append: '.jpg' }}
    Output:
        sales.jpg
    """
    return value + arg


@register.filter
def camelcase(value):
    """Converts a string into CamelCase.
    Input:
        {{ 'coming-soon' | camelcase }}
    Output:
        ComingSoon
    """
    chunks = value.split('-')
    return ''.join([x.title() for x in chunks])


@register.filter
def capitalize(value):
    """Capitalizes the first word in a string.
    Input:
        {{ 'capitalize me' | capitalize }}
    Output:
        Capitalize me
    """
    return value.title()


@register.filter
def downcase(value):
    """Converts a string into lowercase.
    Input
        {{ 'UPPERCASE' | downcase }}
    Output
        uppercase
    """
    return value.lower()


@register.filter
def escape(value):
    """Escapes a string.
    Input
        {{ "<p>test</p>" | escape }}
    Output
         <!-- The <p> tags are not rendered -->
        <p>test</p>"""
    import html
    return html.escape(value)


@register.filter
def upcase(value):
    return value.upper()


# capture tag

@register.tag(name='capture')
def do_capture(parser, token):
    """
    Capture the contents of a tag output.
    Usage:
    .. code-block:: html+django
        {% capture %}..{% endcapture %}                    # output in {{ capture }}
        {% capture silent %}..{% endcapture %}             # output in {{ capture }} only
        {% capture as varname %}..{% endcapture %}         # output in {{ varname }}
        {% capture as varname silent %}..{% endcapture %}  # output in {{ varname }} only
    For example:
    .. code-block:: html+django
        {# Allow templates to override the page title/description #}
        <meta name="description" content="{% capture as meta_description %}{% block meta-description %}{% endblock %}{% endcapture %}" />
        <title>{% capture as meta_title %}{% block meta-title %}Untitled{% endblock %}{% endcapture %}</title>
        {# copy the values to the Social Media meta tags #}
        <meta property="og:description" content="{% block og-description %}{{ meta_description }}{% endblock %}" />
        <meta name="twitter:title" content="{% block twitter-title %}{{ meta_title }}{% endblock %}" />
    """
    bits = token.split_contents()

    # tokens
    t_as = 'as'
    t_silent = 'silent'
    var = 'capture'
    silent = False

    num_bits = len(bits)
    if len(bits) > 4:
        raise template.TemplateSyntaxError("'capture' node supports '[as variable] [silent]' parameters.")
    elif num_bits == 4:
        t_name, t_as, var, t_silent = bits
        silent = True
    elif num_bits == 3:
        t_name, t_as, var = bits
    elif num_bits == 2:
        t_name, t_silent = bits
        silent = True
    else:
        var = 'capture'
        silent = False

    if t_silent != 'silent' or t_as != 'as':
        raise template.TemplateSyntaxError("'capture' node expects 'as variable' or 'silent' syntax.")

    nodelist = parser.parse(('endcapture',))
    parser.delete_first_token()
    return CaptureNode(nodelist, var, silent)


class CaptureNode(template.Node):
    def __init__(self, nodelist, varname, silent):
        self.nodelist = nodelist
        self.varname = varname
        self.silent = silent

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        if self.silent:
            return ''
        else:
            return output
