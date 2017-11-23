# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from navsy import cache
from navsy.utils import import_function, path_utils, pattern_utils, url_utils


def router(request, path=None):

    # force redirect based on settings.APPEND_SLASH value
    path_fixed = path_utils.fix_path(path)

    if path and path != path_fixed:
        fixed_append_slash = path.endswith('/') != path_fixed.endswith('/')
        fixed_double_slash = '//' in path and '//' not in path_fixed
        if fixed_append_slash or fixed_double_slash:
            return HttpResponseRedirect(url_utils.reverse_url(path_fixed))

    path = path_fixed
    # print(path)

    routes_list = cache.get_routes_list()
    routes_list = list(reversed(routes_list))

    for route_data in routes_list:
        route_re = pattern_utils.get_regex_re(
            route_data['page_path'], route_data['regex'])
        route_match = route_re.match(path)
        # print('route match: %s -> %s == %s' % (
        #     True if route_match else False, path, route_re.pattern, ))

        if route_match:
            route_match_kwargs = route_match.groupdict()
            route_match_keys = list(route_match_kwargs.keys())
            route_match_keys.sort(key=lambda arg: route_re.pattern.find(arg))
            route_match_args = [route_match_kwargs[key]
                                for key in route_match_keys]
            # print(route_match_kwargs)
            # print(route_match_keys)
            # print(route_match_args)

            route_data = cache.get_route_data(route_data['pk'])
            # cache.print_data(route_data)
            if route_data.get('published', False):

                page_data = route_data.get('page')
                # cache.print_data(page_data)
                if not page_data or page_data.get('published', False):

                    route_obj = route_data['object']
                    return __route_response(request, route_obj,
                        *route_match_args, **route_match_kwargs)

    raise Http404


def __route_response(request, instance, *args, **kwargs):

    route_obj = instance
    route_data = cache.get_route_data(route_obj.pk)
    # cache.print_data(route_data)

    redirect_url = route_obj.get_redirect_url()
    if redirect_url:
        return HttpResponseRedirect(redirect_url)

    data = {
        'navsy_page': route_obj.page,
        'navsy_route': route_obj,
        'navsy_route_args': args,
        'navsy_route_kwargs': kwargs,
    }

    request.navsy_data = data

    if route_obj.view_template_path:
        return render(request, route_obj.view_template_path)

    if route_obj.view_function_path:
        view_function = import_function(route_obj.view_function_path)
        if view_function:
            if kwargs:
                view_response = view_function(request, **kwargs)
            elif args:
                view_response = view_function(request, *args)
            else:
                view_response = view_function(request)

            if isinstance(view_response, HttpResponse):
                return view_response
            # TODO: return automatic response based on view_response type
            # elif view_response is dict or array, convert it to json and return it
            # elif view_response is bool or number, convert it to string and return it
            else:
                raise Exception('View function "%s" doesn\'t return \
                    an HttpResponse object.' % (route_obj.view_function_path, ))
        else:
            # this should never happen since there is form validation
            raise Exception('View function "%s" is not \
                a valid function.' % (route_obj.view_function_path, ))

    return render(request, 'navsy/default.html')
