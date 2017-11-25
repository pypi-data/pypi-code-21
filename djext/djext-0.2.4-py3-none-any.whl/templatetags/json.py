import json

from django import template

register = template.Library()


def json_encode_base(data, indent=None, ensure_ascii=True):
    try:
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
    except:
        return ''


@register.simple_tag(name='json_encode')
def json_encode(data, indent=None, ensure_ascii=True):
    return json_encode_base(data, indent, ensure_ascii)


@register.assignment_tag(name='to_json')
def to_json(data, indent=None, ensure_ascii=True):
    return json_encode_base(data, indent, ensure_ascii)
