#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections.abc import Iterable
from wtforms.widgets import html_params, HTMLString


class FileDisplayWidget(object):
    html_params = staticmethod(html_params)

    def __init__(self, input_type='string', text=''):
        self.input_type = input_type
        self.text = text

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = [u'<ul %s>' % html_params(id=field.id)]
        data = field.data
        if data:
            if not isinstance(data, Iterable):
                params = dict(href=data)
                html.append(u'<li><a %s>%s</li>' % (html_params(**params), data))
            else:
                for link in data:
                    if link:
                        params = dict(href=link)
                        html.append(u'<li ><a %s>%s</li>' % (html_params(**params), link))
        html.append(u'</ul>')
        return HTMLString(u''.join(html))
