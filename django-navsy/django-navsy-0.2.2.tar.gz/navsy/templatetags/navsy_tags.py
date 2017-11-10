# -*- coding: utf-8 -*-

from django import template
from django.utils.safestring import mark_safe

from navsy import cache, settings
from navsy.exceptions import NoReverseMatch
from navsy.models import Page, Route
from navsy.urls import reverse
from navsy.utils import i18n_utils

try:
    basestring
except NameError:
    basestring = str

register = template.Library()


def __get_context_data(context, data=None):

    request = context.get('request')

    data = data or {}
    data['request'] = request
    data['domain'] = '%s://%s' % (request.scheme, request.get_host(), )
    data['navsy_model'] = context.get('navsy_model', None)
    data.update(dict(request.navsy_data))
    # print(data)
    return data


@register.inclusion_tag('navsy/breadcrumbs.html', takes_context=True)
def navsy_breadcrumbs(context):

    data = __get_context_data(context)

    breadcrumbs = []

    page = data.get('navsy_page')
    if page:
        page_data = cache.get_page_data(page.pk)
        page_pks = page_data.get('path_pks', [])
        for page_pk in page_pks:
            page_data = cache.get_page_data(page_pk)
            page_obj = page_data['object']
            breadcrumbs.append({
                'name': page_obj.name if not page_obj.home else '',
                'url': page_obj.url,
                'active': bool(page_obj == page),
            })

    data['breadcrumbs'] = breadcrumbs

    return data


@register.simple_tag(takes_context=True)
def navsy_is(context, target, yes='', no=''):

    return navsy_is_page(context, target, yes,
                navsy_is_route(context, target, yes,
                    navsy_is_view(context, target, yes, no)))


@register.simple_tag(takes_context=True)
def navsy_is_page(context, page, yes='', no=''):

    if not isinstance(page, Page):
        return no

    data = __get_context_data(context)
    page_obj = data.get('navsy_page', None)
    return yes if page_obj and page_obj == page else no


@register.simple_tag(takes_context=True)
def navsy_is_page_parent(context, page, yes='', no=''):

    if not isinstance(page, Page):
        return no

    data = __get_context_data(context)
    page_obj = data.get('navsy_page', None)
    page_obj_parents_pks = page_obj.get_parents_pks()
    page_pk = getattr(page, 'pk', None)
    return yes if page_obj and page_pk in page_obj_parents_pks else no


@register.simple_tag(takes_context=True)
def navsy_is_route(context, route, yes='', no=''):

    if not isinstance(route, Route):
        return no

    data = __get_context_data(context)
    route_obj = data.get('navsy_route', None)
    return yes if route_obj and route_obj == route else no


@register.simple_tag(takes_context=True)
def navsy_is_view(context, view_name, yes='', no=''):

    if not isinstance(view_name, basestring):
        return no

    data = __get_context_data(context)
    route_obj = data.get('navsy_route', None)
    return yes if route_obj and route_obj.view_name == view_name else no


@register.simple_tag(takes_context=True)
def navsy_language_label(context, language, label=None):

    label = label or context.get('label', None)
    value = ''

    if label == 'code':
        value = language.get('code', '')
        value = value.upper()

    elif label == 'name':
        value = language.get('name_local', '')
        value = value.title()

    elif label == 'short_name':
        value = language.get('name_local', '')
        if len(value) > 3:
            value = value[:3]
        value = value.upper()

    else:
        value = language.get('code', '')
        value = value.upper()

    return value


@register.inclusion_tag(
    'navsy/languages-alternate-href.html', takes_context=True)
def navsy_languages_alternate_href(context, languages=None):

    data = __get_context_data(context)
    data.update({
        'multilanguage': settings.NAVSY_MULTILANGUAGE,
        'languages_filter': i18n_utils.split_languages(languages),
    })
    return data


@register.inclusion_tag(
    'navsy/languages-menu.html', takes_context=True)
def navsy_languages_menu(context, languages=None, label=None, select=False):

    data = __get_context_data(context)
    data.update({
        'multilanguage': settings.NAVSY_MULTILANGUAGE,
        'languages_filter': i18n_utils.split_languages(languages),
        'languages_label': label,
        'languages_select': select,
    })
    return data


@register.inclusion_tag(
    'navsy/menu.html', takes_context=True)
def navsy_menu(context, select=False, label=None, levels=None):

    data = __get_context_data(context)
    nodes_tree = cache.get_nodes_tree()
    # print(nodes_tree)

    data['menu_root'] = True
    data['menu_nodes'] = nodes_tree
    data['menu_select'] = select
    data['menu_label'] = label
    data['menu_level'] = 0
    data['menu_levels'] = levels
    try:
        data['menu_levels'] = int(data['menu_levels'])
    except TypeError:
        data['menu_levels'] = None

    return data


# TODO
# @register.simple_tag(takes_context=True)
# def navsy_page(context, reverse_id=None):
#     pass


@register.simple_tag(takes_context=True)
def navsy_page_label(context, page, label=None):

    label = label or context.get('label', None)
    value = ''

    if label == 'name':
        value = page.name

    elif label == 'flat':
        value = page.name

    elif label == 'path':
        page_data = cache.get_page_data(page.pk)
        value = ' / '.join(page_data['path_names'])

    # elif label == 'tabs':
    #     page_data = cache.get_page_data(page.pk)
    #     if page.parents_count:
    #         value = '&nbsp;' * 4 * page.parents_count + ' '
    #         value = '&nbsp;' * 6 * (page.parents_count - 1) + '&nbsp;|__ '
    #         value = '&nbsp;' * 5 * (page.parents_count - 1) + '&nbsp;\\_ '
    #     value += page.name

    elif label == 'tree':
        page_data = cache.get_page_data(page.pk)
        if page.parents_count:
            value = '&mdash; ' * page.parents_count
        value += page.name

    else:
        value = page.name

    value = mark_safe(value)
    return value


# # TODO: add navsy_pagination templatetag
# @register.inclusion_tag('navsy/pagination.html', takes_context=True)
# def navsy_pagination(context, select=False):
#     pass


@register.simple_tag(takes_context=True)
def navsy_routes(context):

    routes_list = cache.get_routes_list()
    return routes_list


@register.simple_tag(takes_context=True)
def navsy_title(context, default=None, base=None, html=True):

    data = __get_context_data(context)
    page = data.get('navsy_page')

    if page and page.home:
        title = default or base
        title = title.strip()
    else:
        model = data.get('navsy_model')
        titles = []

        if model:
            if hasattr(model, 'title'):
                titles.append(model.title)
            elif hasattr(model, 'name'):
                titles.append(model.name)
            else:
                titles.append(str(model))

        if page:
            names = cache.get_page_data(page.pk).get('path_names', [])
            titles += list(reversed(names))

        title = ' - '.join(titles)

        if base:
            if title:
                title += ' | '
            title += base.strip()
        else:
            title = default or base
            title = title.strip()

    if html:
        title_html = '<title>%s</title>' % (title, )
        title_html = mark_safe(title_html)
        return title_html
    else:
        return title


@register.simple_tag(takes_context=True)
def navsy_url(context, view_name=None, language=None, *args, **kwargs):

    # print(__get_context_data(context))
    url = ''

    if view_name:
        try:
            if kwargs:
                url = reverse(view_name, **kwargs)
            elif args:
                url = reverse(view_name, *args)
            else:
                url = reverse(view_name)
                print(url)

        except KeyError:
            # kwargs contains an argument with an invalid type
            url = reverse(view_name)

        except TypeError:
            # args contains an argument with an invalid type
            url = reverse(view_name)

        except NoReverseMatch:
            pass
    else:

        data = __get_context_data(context)
        model = data.get('navsy_model', None)

        if model:
            url = i18n_utils.call_function_for_language(
                model.get_absolute_url, language)
        else:
            route_language = kwargs.pop('language', None)
            # print(route_language)

            route_obj = data.get('navsy_route', None)
            route_args = data.get('navsy_route_args', [])
            route_kwargs = data.get('navsy_route_kwargs', {})
            # print(route_obj)
            # print(route_args)
            # print(route_kwargs)

            if route_obj:
                url = route_obj.get_absolute_url(
                    language=route_language, parameters=route_kwargs)

        if not url:
            url = '/'

        # append query string
        request = data.get('request')

        if request.GET:

            request_get = request.GET.copy()
            for k in kwargs:
                request_get[k] = kwargs[k]

            url += '?' + request_get.urlencode()

    # print(url)
    return url
