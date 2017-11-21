# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.cache import cache
from django.utils import translation

from navsy.utils import i18n_utils

import json


__data = None


def delete_data():
    # print('delete_data')
    global __data
    __data = None
    cache.delete('navsy_data')


def get_data():
    data = cache.get('navsy_data', None)
    return data


def get_or_create_data():
    # print('get_or_create_data')
    global __data
    if not __data:
        data = get_data()
        if not data:
            data = update_data()
        __data = data
    return __data


def get_or_create_data_for_current_language():
    # print('get_or_create_data_for_current_language')
    data = get_or_create_data()
    lang = i18n_utils.get_current_language()
    return data.get(lang, {})


def get_nodes_dict():
    data = get_or_create_data()
    nodes_dict = data.get('nodes', {})
    return nodes_dict


def get_nodes_tree():
    data = get_or_create_data()
    nodes_tree = data.get('tree', [])
    return nodes_tree


def get_pages_dict():
    lang_data = get_or_create_data_for_current_language()
    pages_dict = lang_data.get('pages_by_pk', {})
    return pages_dict


def get_pages_list():
    data = get_or_create_data()
    pages_dict = get_pages_dict()
    pages_list = [pages_dict.get(str(page_obj.pk))
                  for page_obj in data.get('pages', [])]
    return pages_list


# def get_pages_tree():
#     pass


def get_page_data(page_pk):
    pages_dict = get_pages_dict()
    page_data = dict(pages_dict.get(str(page_pk), {}))
    return page_data


def get_routes_dict():
    lang_data = get_or_create_data_for_current_language()
    routes_dict = lang_data.get('routes_by_pk', {})
    return routes_dict


def get_routes_list():
    data = get_or_create_data()
    routes_dict = get_routes_dict()
    routes_list = [routes_dict.get(str(route_obj.pk))
                   for route_obj in data.get('routes', [])]
    return routes_list


def get_route_data(route_pk):
    routes_data = get_routes_dict()
    route_data = dict(routes_data.get(str(route_pk), {}))
    page_data = get_page_data(route_data.get('page_pk'))
    route_data['page'] = page_data
    return route_data


def get_route_data_by_view_name(view_name):
    data = get_or_create_data()
    routes_by_view_name_dict = data['routes_by_view_name']
    route_obj = routes_by_view_name_dict.get(view_name)
    route_data = get_route_data(route_obj.pk) if route_obj else None
    return route_data


def set_data(data):
    # print('set_data')
    global __data
    cache.set('navsy_data', data, None)
    __data = data


def print_data(data):#language=None):
    # print('print_data')
    try:
        data = json.dumps(data, indent=4)
    except TypeError:
        pass
    print(data)


def serialize_data():
    # print('serialize_data')
    from .models import Page, Route

    if settings.DEBUG:
        import timeit
        start_time = timeit.default_timer()

    data = {}

    pages_qs = Page.objects.all()
    pages_list = list(pages_qs)

    routes_qs = Route.objects.select_related('pattern', 'page').all()
    routes_list = list(routes_qs)
    routes_by_view_name = { obj.view_name:obj
        for obj in routes_list if obj.view_name }

    nodes_dict = { str(obj.pk):{
            'object':obj,
            'pk':obj.pk,
            'parents_pks':obj.get_parents_pks(),
            'children_pks':obj.get_children_pks(),
            'siblings_pks':obj.get_siblings_pks(),
            'level': len(obj.get_parents_pks()) + 1,
        } for obj in pages_list }

    nodes_tree = []

    def serialize_node_tree(node_data):
        node_children_pks = list(node_data['children_pks'])
        node_data['children'] = []

        # # uncomment for debug
        # node_data['name'] = node_data['object'].name
        # node_data.pop('object', None)
        # node_data.pop('parents_pks', None)
        # node_data.pop('children_pks', None)
        # node_data.pop('siblings_pks', None)

        for node_child_pk in node_children_pks:
            node_child_data = dict(nodes_dict[str(node_child_pk)])
            node_child_tree = serialize_node_tree(node_child_data)
            node_data['children'].append(node_child_tree)
        return node_data

    #print(len(pages_list))
    for page_obj in pages_list:
        # print(page_obj)
        node_data = dict(nodes_dict[str(page_obj.pk)])
        node_parents_pks = node_data['parents_pks']
        if len(node_parents_pks):
            continue
        # print(node_data['object'], len(node_parents_pks))
        node_tree = serialize_node_tree(node_data)
        nodes_tree.append(node_tree)

    # print_data(nodes_tree)

    data['nodes'] = nodes_dict
    data['tree'] = nodes_tree
    data['pages'] = pages_list
    data['routes'] = routes_list
    data['routes_by_view_name'] = routes_by_view_name

    active_language = i18n_utils.get_current_language()

    for language in settings.LANGUAGES:

        language_code = language[0]
        translation.activate(language_code)
        language_key = language_code
        # print(language_key.upper())

        data[language_key] = {
            'pages_by_pk': {},
            'routes_by_pk': {},
        }

        data_pages_by_pk = data[language_key]['pages_by_pk']
        data_routes_by_pk = data[language_key]['routes_by_pk']

        for page_obj in pages_list:
            page_key = str(page_obj.pk)
            page_node = data['nodes'][page_key]
            page_data = {
                'object': page_obj,
                'path_pks': [],
                'path_names': [],
                'path_slugs': [],
                'path': '',
                'menu': True,
                'published': True,
            }

            for page_parent_pk in page_node['parents_pks']:
                page_parent_obj = data['nodes'][str(page_parent_pk)]['object']
                if page_parent_obj.home:
                    continue
                page_data['path_pks'].append(page_parent_obj.pk)
                page_data['path_names'].append(page_parent_obj.name)
                page_data['path_slugs'].append(page_parent_obj.slug)
                page_data['menu'] = bool(
                    page_data['menu'] and page_parent_obj.menu)
                page_data['published'] = bool(
                    page_data['published'] and page_parent_obj.published)

            page_data['path_pks'].append(page_obj.pk)
            page_data['path_names'].append(page_obj.name)
            page_data['path_slugs'].append(page_obj.slug if not page_obj.home else '')

            page_path = '/'.join(page_data['path_slugs'])
            page_data['path'] = page_path
            page_data['routes'] = []
            # print(page_data)

            data_pages_by_pk[page_key] = page_data

        for route_obj in routes_list:
            route_key = str(route_obj.pk)
            route_pattern = route_obj.pattern
            route_page = route_obj.page
            route_page_key = str(route_page.pk) if route_page else ''
            route_page_data = data_pages_by_pk.get(route_page_key, None)
            if route_page_data:
                route_page_data['routes'].append(route_key)

            route_regex = route_pattern.regex
            route_regex_display = route_pattern.regex_display
            route_regex_format = route_pattern.regex_format
            route_page_path = route_page_data['path'] if route_page_data else ''
            route_data = {
                'object': route_obj,
                'pk': route_key,
                'page_pk': route_page_key,
                'page_path': route_page_path,
                'regex': route_regex,
                'regex_display': route_regex_display if route_regex else '',
                'regex_format': route_regex_format,
                'published': route_obj.published,
            }

            # print(route_data)

            data_routes_by_pk[route_key] = route_data

    translation.activate(active_language)

    if settings.DEBUG:
        elapsed = timeit.default_timer() - start_time
        print('navsy.cache -> serialize_data in %ss' % (elapsed, ))

    return data


def update_data():
    # print('update_data')
    data = serialize_data()
    set_data(data)
    return data
