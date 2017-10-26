#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午3:25
# @Author  : Hou Rong
# @Site    : 
# @File    : Web.py
# @Software: PyCharm
import re
import functools
import vine.five

if vine.five.PY2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


def soap_body(soap_action):
    def wrapper(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            return '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"><soap:Header/><soap:Body>' \
                   '<{1} versionNumber="7.0">' \
                   '{0}</{1}></soap:Body></soap:Envelope>'.format(func(*args, **kwargs), soap_action)

        return f

    return wrapper


def modify_url(raw_url):
    """
    :type raw_url: str
    :return: str
    """
    if not bool(re.match(r'^https?:/{2}\w.+$', raw_url or '')):
        return ''

    parsed_obj = urlparse(raw_url.strip())

    parsed_link_prefix = '{0}://{1}{2}'.format(
        parsed_obj.scheme.strip(),
        parsed_obj.netloc.strip(),
        parsed_obj.path.strip(),
    )
    if parsed_obj.query:
        parsed_link = "{0}?{1}".format(parsed_link_prefix, parsed_obj.query.strip())
    else:
        parsed_link = parsed_link_prefix
    return parsed_link
