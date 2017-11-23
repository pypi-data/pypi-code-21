# -*- coding: utf-8 -*-


def data(request):
    d = {}
    if request:
        d['navsy_base_url'] = '%s://%s' % (request.scheme, request.get_host(), )
        d.update(getattr(request, 'navsy_data', {}))
    return d
