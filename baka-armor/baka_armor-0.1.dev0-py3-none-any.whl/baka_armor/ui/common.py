"""
 # Copyright (c) 07 2016 | suryakencana
 # 7/10/16 nanang.ask@kubuskotak.com
 #  common
"""
from datetime import datetime
import json

from webhelpers2.html import tags, HTML
from webhelpers2.misc import NotGiven

from .utils import gen_id as _gen_id, date_now as _date_now, format_decimal as _f_dec


def gen_id(prefix=u'obj', limit=6):
    return _gen_id(prefix, limit)


def reset(name, value=None, fid=NotGiven, **attrs):
    return tags.text(name, value, fid, type="reset", **attrs)


def error_container(name, as_text=False):
    return HTML.tag(
        'span',
        class_='error %s hidden'
               % ('fa fa-arrow-circle-down as-text' if as_text else 'fa fa-exclamation-circle'),
        **{'data-name': name}
    )


def button(context, permision, caption, **kwargs):
    html = ''
    if context.has_permision(permision):
        caption = HTML.tag('span', c=caption)
        icon = ''
        if 'icon' in kwargs:
            icon = HTML.tag('span', class_=kwargs.pop('icon'))
        button_class = "button _action " + kwargs.pop('class', '')
        button_class = button_class.strip()
        html = HTML.tag(
            'a', class_=button_class,
            c=HTML(icon, caption), **kwargs
        )
    return html


def jsonify(val):
    return json.dumps(val)


def contact_type_icon(contact_type):
    assert contact_type.key in (u'phone', u'email', u'skype'), \
        u"wrong contact type"
    if contact_type.key == u'phone':
        return HTML.tag('span', class_='fa fa-phone')
    elif contact_type.key == u'email':
        return HTML.tag('span', class_='fa fa-envelope')
    else:
        return HTML.tag('span', class_='fa fa-skype')


def date_now(format_="%d.m.%Y %H:%M:%S"):
    return _date_now(format_)


def today():
    return datetime.today().date()


def format_decimal(value, quantize='.01'):
    return _f_dec(value, quantize)
