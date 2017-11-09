import json
import re

import jinja2
import jinja2.ext
from django.conf import settings
from django.contrib.messages.context_processors import get_messages
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.forms.utils import flatatt
from django.template.defaultfilters import linebreaks_filter, linebreaksbr
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from wagtail.wagtailcore.models import Page


def add_form_class(bound_field, new_classes):
    """Add a class to a django form field widget"""
    attrs = bound_field.field.widget.attrs
    classes = sorted(set(attrs.get('class', '').split() + new_classes.split()))
    attrs['class'] = ' '.join(classes)
    return bound_field


def add_form_attributes(bound_field, attributes={}):
    """Add 1 or more attributes to a django form field widget"""
    bound_field.field.widget.attrs.update(attributes)
    return bound_field


def include_static(path):
    """
    Include the contents of a file that has been compiled into the static directory
    """
    fullpath = finders.find(path)
    if fullpath is None:
        raise ValueError("Could not find file %s" % path)

    with open(fullpath, "r") as f:
        return f.read()


def debug_variable(variable):
    """Print all the fields available on a variable"""
    return format_html('<pre>{}</pre>', dir(variable))


@jinja2.contextfunction
def csrf_field(context):
    """Print the hidden CSRF token field"""
    csrf_token = context.get('csrf_token')
    if not csrf_token or csrf_token == 'NOTPROVIDED':
        return format_html("")

    return format_html("<input{}>", flatatt({
        'type': 'hidden',
        'name': 'csrfmiddlewaretoken',
        'value': csrf_token}))


def url(name, *args, **kwargs):
    """Reverse a URL name. Alias of ``django.core.urlresolvers.reverse``"""
    return reverse(name, args=args or None, kwargs=kwargs or None)


@jinja2.contextfunction
def site_root(context):
    """Get the root page for the site"""
    # This lookup will be cached on the intermediary objects, so this will only
    # hit the DB once per request
    return context['request'].site.root_page.specific


def svg_inline(name):
    """
    Inline an SVG image. SVG images are expected to be a template, not kept in
    the static files
    """
    return mark_safe(render_to_string('svgs/%s.svg' % name))


@jinja2.contextfunction
def breadcrumbs(context, page=None):
    """Print the top navigation menu for this site"""
    request = context.get('request')
    root = site_root(context)
    if page is None:
        page = context.get('page')
    ancestors = page.get_ancestors().filter(depth__gte=root.depth)

    return jinja2.Markup(render_to_string('tags/breadcrumbs.html', {
        'page': page,
        'ancestors': ancestors,
        'request': request,
    }))


def js_context(key, value):
    """ Adds variables to the window for use by other scripts. """
    return format_html('window.appData["{0}"] = {1};'.format(key.upper(), json.dumps(value)))


def model_classname(model_or_instance):
    """
    Generate a CSS class name from a Page model

    Usage::

        <html class="{{ self|model_classname }}">
    """
    if isinstance(model_or_instance, Page):
        model_or_instance = model_or_instance.content_type.model_class()

    try:
        meta = model_or_instance._meta
        return 'page-{0}-{1}'.format(meta.app_label, meta.model_name)
    except AttributeError:
        return ''


@jinja2.contextfunction
def messages(context):
    """Get any messages from django.contrib.messages framework"""
    return get_messages(context.get('request'))


def json_dumps(value):
    """
    Dump the value to a JSON string. Useful when sending values to JavaScript
    """
    return jinja2.Markup(json.dumps(value, cls=DjangoJSONEncoder))


@jinja2.contextfunction
def qs(context, get=None, **kwargs):
    """
    Update a querydict with new values, and return it as a URL encoded string.
    Pass in the current ``request.GET``, and any items to set as keyword
    arguments. If a key has a value of ``None``, that key is removed from the
    querydict.

    The querydict is grabbed from ``request`.GET` in the context by default,
    but an alternative can be provided as the first positional argument.

    >>> request.GET.urlencode()
    "page=1&foo=bar"
    >>> qs(request.GET, page=2, baz="quux", foo=None)
    "page=2&baz=quux"
    """
    if get is None:
        get = context['request'].GET

    get = get.copy()
    for key, value in kwargs.items():
        if value is None:
            # Delete keys if value is None
            get.pop(key, None)
        else:
            get[key] = value
    return get.urlencode()


not_digit_re = re.compile(r'[^0-9+]+')


def tel(value):
    return 'tel:{}'.format(not_digit_re.sub('-', value).strip('-'))


def date(date, format):
    """
    Print a date using the format after localising it to the current timezone.

    Assuming the time is currently 9am on 2017-05-17 in Australia/Hobart:

    >>> d = timezone.now()
    datetime.datetime(2017, 5, 16, 23, 0, 0, tzinfo=<UTC>)
    >>> d.strftime("%Y-%m-%d %H:%M:%S")
    "2017-05-16 23:00:00"
    >>> date(d, "%Y-%m-%d %H:%M:%S")
    "2017-05-17 09:00:00"
    """
    if not date:
        raise ValueError('No date supplied')
    if timezone.is_naive(date):
        date = timezone.make_aware(date)
    return timezone.localtime(date).strftime(format)


class Extension(jinja2.ext.Extension):
    def __init__(self, environment):
        super(Extension, self).__init__(environment)

        self.environment.globals.update({
            'breadcrumbs': breadcrumbs,
            'site_root': site_root,
            'csrf_field': csrf_field,
            'static': staticfiles_storage.url,
            'include_static': include_static,
            'url': url,
            'svg': svg_inline,
            'js_context': js_context,
            'model_classname': model_classname,
            'messages': messages,
            'DEBUG': settings.DEBUG,
            'qs': qs,
        })

        self.environment.filters.update({
            'model_classname': model_classname,
            'add_form_class': add_form_class,
            'add_form_attributes': add_form_attributes,
            'debug_variable': debug_variable,
            'br': linebreaksbr,
            'p': linebreaks_filter,
            'json': json_dumps,
            'tel': tel,
            'date': date,
        })
