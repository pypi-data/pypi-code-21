# -*- coding: utf-8 -*-


def data(request):
    return request.navsy_data if request and hasattr(
        request, 'navsy_data') else {}
