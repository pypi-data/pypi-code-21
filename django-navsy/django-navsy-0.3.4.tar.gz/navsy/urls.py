# -*- coding: utf-8 -*-

from django.conf.urls import url

from navsy import cache
from navsy.exceptions import NoReverseMatch
from navsy.views import router


def reverse(view_name, *args, **kvargs):

    if args and kvargs:
        raise Exception('reverse cannot receive both *args and **kvargs')
    elif args:
        parameters = list(args)
    elif kvargs:
        parameters = dict(kvargs)
    else:
        parameters = None

    # print('reverse parameters: %s' % (parameters, ))

    route_data = cache.get_route_data_by_view_name(view_name)
    if route_data:
        route_obj = route_data['object']
        return route_obj.get_absolute_url(language=None, parameters=parameters)

    raise NoReverseMatch()


urlpatterns = [
    url(r'(?:(?P<path>.*))?$', router, name='navsy-router'),
]
