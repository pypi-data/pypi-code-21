#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from ..compat import p3_str, p3_chr
from .tools import (
    strip,
    strip_code,
    parse,
    DefaultList,
    title_parts,
    html_unescape,
    str2wikicode,
    query_encode,
    title_encode,
    anchor_encode,
    reindex_params,
    join_title,
)
from .expr import wikieval

import mwparserfromhell as mw
#from mwparserfromhell.nodes import Text

import os
import math
import re
from datetime import datetime


PF_NAME_SEPARATOR = p3_chr(31)


NOT_IMPLEMENTED = (
    "#invoke",
    "#ifexpr",
    "#iferror",
    #"#time",
    #"#timel",
    "subst",
    "safesubst",
)


def _strip_outcome(x):
    if isinstance(x, mw.nodes.extras.Parameter) and not x.showkey:
        return strip_code(x.value)
    return parse(strip(x))


def as_parser_function(name, params):
    str_name = p3_str(name)
    if strip(str_name).endswith(PF_NAME_SEPARATOR):
        name = str_name[:-1].lower()  # str2wikicode(str_name[:-1].lower())
        param0 = params[0]
        # corner case: {{subst:=}}
        if param0.showkey and p3_str(param0) == "=":
            param0.name = str2wikicode("1")
            param0.value = str2wikicode("=")
            param0.showkey = False
            reindex_params(params[1:], 1)
        return mw.nodes.Template(name, params)

    parts = str_name.split(":", 1)

    if len(parts) > 1:
        name = strip(parts[0]).lower()  # mw.parse(strip(parts[0]).lower())
        firstArg = parse(parts[1])
        firstArg = mw.nodes.extras.parameter.Parameter(
            str2wikicode("1"),
            firstArg,
            showkey=False)
        #return mw.nodes.Template(name, [firstArg] + params)
        return mw.nodes.Template(name, [firstArg] + reindex_params(params, 1))

    return None


def as_template(pf):
    if pf.params:
        param0 = p3_str(pf.params.pop(0))
    else:
        param0 = ""
    name = "%s:%s" % (p3_str(pf.name), param0)

    reindex_params(pf.params, -1)

    pf.name = parse(name)

    return pf


def sharp_expr(wikicode, f):
    "{{#expr}}"
    params = DefaultList(wikicode.params, transform=f)

    expr = strip(params.transform(0))

    if expr:
        try:
            out = wikieval(expr)
        except (SyntaxError, NotImplementedError):
            raise NotImplementedError(p3_str(wikicode))
    else:
        out = ""

    return str2wikicode(out)


def sharp_if(wikicode, f):
    "{{#if:}}"
    params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

    test = strip(params.transform(0))

    branch = 1 if test else 2

    out = params.transform(branch)

    return _strip_outcome(out)


def sharp_ifeq(wikicode, f):
    "{{#ifeq:}}"
    params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

    lvalue = strip(params.transform(0))
    rvalue = strip(params.transform(1))

    # try numerical comparison
    try:
        lvalue, rvalue = float(lvalue), float(rvalue)
    except ValueError:
        pass

    branch = 2 if lvalue == rvalue else 3

    out = params.transform(branch)

    return _strip_outcome(out)


def sharp_tag(wikicode, f):
    "{{#tag:}}"
    params = DefaultList(wikicode.params, transform=f)

    name = strip(params.transform(0))
    body = params.transform(1)

    return parse("<{0}>{1}</{0}>".format(name, body))


def sharp_switch(wikicode, f):
    "{{#switch:}}"
    #noptions = len(wikicode.params)

    params = DefaultList(wikicode.params, transform=f)

    test = html_unescape(strip(params.transform(0)))

    try:
        test = float(test)
        is_numeric = True
    except ValueError:
        is_numeric = False

    rev_params = list(reversed(wikicode.params[1:]))

    default = mw.parse(None)

    if not rev_params:
        return default

    last = rev_params[0]

    if not last.showkey:
        default = last.value
        rev_params = rev_params[1:]

    # options
    options = {}
    last_value = mw.parse(None)
    for param in rev_params:
        if param.showkey:
            key = param.name
            value = param.value
            last_value = value
        else:
            # stacked result
            key = param.value
            value = last_value
        key = html_unescape(strip(f(key)))
        if is_numeric:
            try:
                key = float(key)
            except ValueError:
                pass
        options[key] = value

    if "#default" in options:
        default = options["#default"]
        del options["#default"]

    out = f(options.get(test, default))

    return strip_code(out)


def lc(wikicode, f):
    "{{lc:}}"
    params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

    return parse(strip(params.transform(0)).lower())


def uc(wikicode, f):
    "{{uc:}}"
    params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

    return parse(strip(params.transform(0)).upper())


def lcfirst(wikicode, f):
    "{{lcfirst:}}"
    params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

    text = strip(params.transform(0))

    return parse(text[:1].lower() + text[1:])


def ucfirst(wikicode, f):
    "{{ucfirst:}}"
    params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

    text = strip(params.transform(0))

    return parse(text[:1].upper() + text[1:])


def _pad_string(wikicode, f):
    params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

    text = strip(params.transform(0))
    try:
        max_len = int(strip(params.transform(1)))
    except ValueError:
        max_len = len(text)
    pad = strip(f(params.get(2, "0")))

    lpad = len(pad)

    dif = max(max_len - len(text), 0)

    repeats = int(math.ceil(dif / lpad))
    padtext = pad * repeats

    return text, padtext[:dif]


def padleft(wikicode, f):
    "{{padleft:}}"
    text, padding = _pad_string(wikicode, f)

    return parse(padding + text)


def padright(wikicode, f):
    "{{padright:}}"
    text, padding = _pad_string(wikicode, f)

    return parse(text + padding)


def defaultsort(wikicode, f):
    "{{defaultsort:}}"
    return mw.parse(None)


def urlencode(wikicode, f):
    "{{urlencode:}}"
    params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

    text = strip(params.transform(0))

    return str2wikicode(query_encode(text))


def anchorencode(wikicode, f):
    "{{anchorencode:}}"
    params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

    text = strip(params.transform(0))

    return str2wikicode(anchor_encode(text))


class ParserFunction(object):
    """
    Render parser functions given a page context.
    """

    def __init__(self, page_context, time=None):
        self._context = page_context

        self.functions = {
            # flow control
            "#if": sharp_if,
            "#ifeq": sharp_ifeq,
            "#switch": sharp_switch,
            "#ifexist": self.sharp_ifexist,
            "#tag": sharp_tag,
            "#expr": sharp_expr,
            # string manipulation
            "lc": lc,
            "lcfirst": lcfirst,
            "uc": uc,
            "ucfirst": ucfirst,
            "padleft": padleft,
            "padright": padright,
            # url related
            "ns": self.ns,
            "#rel2abs": self.sharp_rel2abs,
            "pagename": self.pagename,
            "fullpagename": self.fullpagename,
            "pagenamee": self.pagenamee,
            "fullpagenamee": self.fullpagenamee,
            "namespace": self.namespace,
            "talkspace": self.talkspace,
            "articlespace": self.articlespace,
            "subjectspace": self.articlespace,
            "namespacee": self.namespacee,
            "talkspacee": self.talkspacee,
            "talkpagename": self.talkpagename,
            "talkpagenamee": self.talkpagenamee,
            "articlespacee": self.articlespacee,
            "subjectspacee": self.articlespacee,
            "fullurl": self.fullurl,
            "defaultsort": defaultsort,
            "urlencode": urlencode,
            "anchorencode": anchorencode,
            "basepagename": self.basepagename,
            "basepagenamee": self.basepagenamee,
            "rootpagename": self.rootpagename,
            "rootpagenamee": self.rootpagenamee,
            "#titleparts": self.sharp_titleparts,
            "subpagename": self.subpagename,
            "subpagenamee": self.subpagenamee,
            "articlepagename": self.articlepagename,
            "articlepagenamee": self.articlepagenamee,
            "subjectpagename": self.articlepagename,
            "subjectpagenamee": self.articlepagenamee,
            # time
            "#time": self.sharp_time,
            "#timel": self.sharp_time,
        }

        names = list(self.functions.keys()) + list(NOT_IMPLEMENTED)
        names += [x.upper() for x in names]
        self._names = tuple(names)
        self._PF_NAME = re.compile(r"({{)\s*(%s)\s*(:)" % "|".join(names))

        self.aux_time = time or datetime.utcnow()

    def prepare(self, text):
        """
        Since parser function parsing is not implemented in mwparserfromhell,
        some cases are not returned as templates. For example:

        {{#if: [[foo]] | [[foo]] | equal | not equal }}

        Detected parser function separator is replaced by ASCII unit separator
        plus a parameter separator (|)

        This trick only works when the name of ther parser function
        has been previously expanded, but I can live with that.
        """
        return self._PF_NAME.sub(
            r"\1\2" + PF_NAME_SEPARATOR + "|",
            p3_str(text)
        )

    def __call__(self, name, *args, **kwargs):
        if name in NOT_IMPLEMENTED:
            raise NotImplementedError(name)

        if name in self.functions:
            return self.functions[name](*args, **kwargs)

        raise KeyError(name)

    def sharp_rel2abs(self, wikicode, f):
        "{{#rel2abs:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        path = strip(params.transform(0))
        if path.startswith(os.path.sep):
            path = "." + path

        if not path.startswith("."):
            return parse(path)

        if len(wikicode.params) < 2:
            basepath = self._context.title()
        else:
            basepath = strip(params.transform(1))

        out = os.path.relpath(os.path.join(basepath, path))

        return str2wikicode(out)

    def ns(self, wikicode, f):
        "{{ns:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        name = self._context.site_context().namespace_normalize(value)

        return str2wikicode(name)

    def sharp_ifexist(self, wikicode, f):
        "{{#ifexist:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))

        branch = 1 if self._context.site_context().page_exists(value) else 2

        return _strip_outcome(params.transform(branch))

    def str_namespace(self, title):
        return self._context.site_context().namespace_name(title)

    def str_namespacee(self, title):
        return title_encode(self.str_namespace(title))

    def namespace(self, wikicode, f):
        "{{NAMESPACE:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_namespace(value)

        return str2wikicode(out)

    def namespacee(self, wikicode, f):
        "{{NAMESPACEE:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_namespacee(value)

        return str2wikicode(out)

    def str_pagename(self, title):
        return self._context.site_context().clean_title(title)

    def str_pagenamee(self, title):
        return title_encode(self.str_pagename(title))

    def pagename(self, wikicode, f):
        "{{PAGENAME:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_pagename(value)

        return str2wikicode(out)

    def pagenamee(self, wikicode, f):
        "{{PAGENAMEE:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_pagenamee(value)

        return str2wikicode(out)

    def str_fullpagename(self, title):
        return self._context.site_context().canonical_title(title)

    def str_fullpagenamee(self, title):
        return title_encode(self.str_fullpagename(title))

    def fullpagename(self, wikicode, f):
        "{{FULLPAGENAME:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_fullpagename(value)

        return str2wikicode(out)

    def fullpagenamee(self, wikicode, f):
        "{{FULLPAGENAMEE:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_fullpagenamee(value)

        return str2wikicode(out)

    def str_talkspace(self, title):
        ns_part, _ = title_parts(title)
        namespace = self._context.site_context().namespace_name(ns_part)
        return self._context.site_context().talkspace(namespace)

    def str_talkspacee(self, title):
        return title_encode(self.str_talkspace(title))

    def talkspace(self, wikicode, f):
        "{{TALKSPACE:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_talkspace(value)

        return str2wikicode(out)

    def talkspacee(self, wikicode, f):
        "{{TALKSPACEE:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_talkspacee(value)

        return str2wikicode(out)

    def str_talkpagename(self, title):
        return self._context.site_context().talkpagename(title)

    def talkpagename(self, wikicode, f):
        "{{TALKPAGENAME:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_talkpagename(value)

        return str2wikicode(out)

    def str_talkpagenamee(self, title):
        return title_encode(self._context.site_context().talkpagename(title))

    def talkpagenamee(self, wikicode, f):
        "{{TALKPAGENAMEE:}}"
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_talkpagenamee(value)

        return str2wikicode(out)

    def str_articlespace(self, title):
        ns_part, _ = title_parts(title)
        namespace = self._context.site_context().namespace_name(ns_part)
        return self._context.site_context().articlespace(namespace)

    def str_articlespacee(self, title):
        return title_encode(self.str_articlespace(title))

    def articlespace(self, wikicode, f):
        """
        {{ARTICLESPACE:}}
        {{SUBJECTSPACE:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_articlespace(value)

        return str2wikicode(out)

    def articlespacee(self, wikicode, f):
        """
        {{ARTICLESPACEE:}}
        {{SUBJECTSPACEE:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_articlespacee(value)

        return str2wikicode(out)

    def fullurl(self, wikicode, f):
        """
        {{fullurl:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self._context.site_context().fullurl(value)

        return str2wikicode(out)

    def sharp_time(self, wikicode, f):
        """
        WARNING: simplified and unreliable implementation
        """
        return str2wikicode(self.aux_time.isoformat())

    def str_titleparts(self, title, n_segments=0, from_segment=0, normalize=True):
        if normalize:
            title = self._context.site_context().canonical_title(title)

        # adjust to base 0
        # when negative, it is already in base 1
        if from_segment > 0:
            from_segment -= 1

        sep = self._context.site_context().SUBPAGE_SEPARATOR

        parts = title.split(sep)

        parts = parts[from_segment:]
        if n_segments:
            parts = parts[:n_segments]

        return sep.join(parts)

    def sharp_titleparts(self, wikicode, f):
        """
        {{#titleparts:<number of segments to return>|<first segment to return>}}

        base-1
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))

        # number of segments
        try:
            n_segments = int(strip(params.transform(1)))
        except ValueError:
            n_segments = 0

        # from segment
        try:
            from_segment = int(strip(params.transform(2)))
        except ValueError:
            from_segment = 0

        out = self.str_titleparts(value, n_segments, from_segment)

        return str2wikicode(out)

    def str_basepagename(self, value):
        # check if the namespace has subpages
        ns, name = self._context.site_context().split_title(value, normalize=True)
        title = join_title(ns, name)

        if self._context.site_context().has_subpages(ns):
            return self.str_titleparts(name, -1, normalize=False)

        return title

    def str_basepagenamee(self, value):
        return title_encode(self.str_basepagename(value))

    def basepagename(self, wikicode, f):
        """
        {{BASEPAGENAME:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))

        out = self.str_basepagename(value)

        return str2wikicode(out)

    def basepagenamee(self, wikicode, f):
        """
        {{BASEPAGENAMEE:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))

        out = self.str_basepagenamee(value)

        return str2wikicode(out)

    def str_rootpagename(self, value):
        # check if the namespace has subpages
        ns, name = self._context.site_context().split_title(value, normalize=True)
        title = join_title(ns, name)

        if self._context.site_context().has_subpages(ns):
            return self.str_titleparts(name, 1, normalize=False)

        return title

    def str_rootpagenamee(self, value):
        return title_encode(self.str_rootpagename(value))

    def rootpagename(self, wikicode, f):
        """
        {{ROOTPAGENAME:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))

        out = self.str_rootpagename(value)

        return str2wikicode(out)

    def rootpagenamee(self, wikicode, f):
        """
        {{ROOTPAGENAMEE:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))

        out = self.str_rootpagenamee(value)

        return str2wikicode(out)

    def str_subpagename(self, value):
        # check if the namespace has subpages
        ns, name = self._context.site_context().split_title(value, normalize=True)
        title = join_title(ns, name)

        if self._context.site_context().has_subpages(ns):
            return self.str_titleparts(name, from_segment=-1, normalize=False)

        return title

    def str_subpagenamee(self, value):
        return title_encode(self.str_subpagename(value))

    def subpagename(self, wikicode, f):
        """
        {{SUBPAGENAME:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))

        out = self.str_subpagename(value)

        return str2wikicode(out)

    def subpagenamee(self, wikicode, f):
        """
        {{SUBPAGENAMEE:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))

        out = self.str_subpagenamee(value)

        return str2wikicode(out)

    def str_articlepagename(self, title):
        return self._context.site_context().articlepagename(title)

    def articlepagename(self, wikicode, f):
        """
        {{ARTICLEPAGENAME:}}
        {{SUBJECTPAGENAME:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_articlepagename(value)

        return str2wikicode(out)

    def str_articlepagenamee(self, title):
        return title_encode(self._context.site_context().articlepagename(title))

    def articlepagenamee(self, wikicode, f):
        """
        {{ARTICLEPAGENAMEE:}}
        {{SUBJECTPAGENAME:}}
        """
        params = DefaultList(wikicode.params, default=mw.parse(None), transform=f)

        value = strip(params.transform(0))
        out = self.str_articlepagenamee(value)

        return str2wikicode(out)
