"""
 # Copyright (c) 07 2016 | suryakencana
 # 7/2/16 nanang.ask@kubuskotak.com
 #  helpers
"""
from ..ui import common
from ..ui import fields

from webhelpers2.html import tags
from webhelpers2.html import builder


def title(title, required=False, label_for=None):
    """ label helper
    """
    title_html = title

    required_symbol = ''
    _class = None

    if required:
        _class = "required"
        required_symbol = builder.HTML.span("*", class_="required-symbol")

    if label_for:
        title_html = builder.HTML.label(
            title_html,
            " ",
            required_symbol,
            for_=label_for)

    return builder.HTML.span(title_html, class_=_class)

tags.title = title
