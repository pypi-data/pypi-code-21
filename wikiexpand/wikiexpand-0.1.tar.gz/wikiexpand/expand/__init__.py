#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Expansion engine for expanding text using MediaWiki syntax.
"""

from __future__ import (
    unicode_literals,
    print_function,
    absolute_import
)

from ..compat import p3_str
from . import parser_functions as PF
from .context import PageContext

from .tools import (
    strip,
    strip_code,
    reindex_params,
    str2wikicode,
    parse
)
from .templates import TemplateDict

import mwparserfromhell as mw
from mwparserfromhell.nodes import (
    Argument,
    Comment,
    Heading,
    Tag,
    Template,
    Text,
    Wikilink
)
from mwparserfromhell.nodes.extras import (
    Parameter,
    Attribute
)
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.smart_list import SmartList

from functools import partial
from collections import deque
import sys


_EMPTY = mw.parse(None)


_PARSER_FUNCTION_MODE = 0
_SUBST_MODE = 1
_INVOKE_MODE = 2


_PF_MODE = {
    "subst": _SUBST_MODE,
    "safesubst": _SUBST_MODE,
    "#invoke": _INVOKE_MODE,
}


def _append(collection, node):
    if isinstance(node, Wikicode):
        collection.extend(node.nodes)
    else:
        collection.append(node)


class ExpansionContext(object):

    MAX_RECURSION = 70

    def __init__(self, templates=None, page_context=None, *args, **kwargs):
        """
        Create an expansion context for a page.

        To expand a template, a template store providing the body of
        the template is required.

        To expand contextual magic words, a page context providing information
        about the page and the site is required.

        :param templates: a template store
        :type templates: :class:`wikiexpand.expand.context.TemplateStore`

        :param page_context: a page context provider
        :type page_context: :class:`wikiexpand.expand.context.PageContext`
        """
        self._cache_pre = {}
        self._cache_post = {}
        self.templates = TemplateDict() if templates is None else templates
        self.set_context(page_context)

        self._action = {
            Argument: self._expand_argument,
            Comment: self._expand_comment,
            Tag: self._expand_tag,
            Template: self._expand_template,
            Wikilink: self._expand_wikilink,
            Heading: self._expand_heading,
        }

        self._substitute_template = partial(self._expand_template, mode=_SUBST_MODE)

        self._action_subst = {
            Argument: partial(self._expand_argument, fn=self._substitute),
            Tag: partial(self._expand_tag, fn=self._substitute),
            Wikilink: partial(self._expand_wikilink, fn=self._substitute),
            Heading: partial(self._expand_heading, fn=self._substitute),
            Template: self._substitute_template,
        }

    def set_context(self, page_context):
        """
        Set a new page context.

        :param page_context: a page context provider
        :type page_context: :class:`wikiexpand.expand.context.PageContext`

        As a side effect, all the previously cached content will be purged.
        """
        self._cache_pre.clear()
        self._cache_post.clear()
        self.context = PageContext() if page_context is None else page_context

        self.parser_function = self.context.parser_functions
        self.magic_words = self.context.magic_words

    def expand(self, wikitext, *args, **kwargs):
        """
        Expand the given wikitext.

        :param wikitext: text formatted using MediaWiki syntax
        :type wikitext: :class:`mwparserfromhell.wikicode.Wikicode` or string

        :rtype: expanded wikicode, as :class:`mwparserfromhell.wikicode.Wikicode`
        """
        wikitext = self.parser_function.prepare(wikitext)
        return self._expand(wikitext, *args, **kwargs)

    def _expand(self, wikitext, arguments=None, level=0):
        """
        """
        if not arguments:
            arguments = {}

        tree = parse(wikitext)

        nodes = deque()

        for node in tree.nodes:
            action = self._action.get(type(node))
            if action:
                action(node, arguments=arguments, level=level, parent=nodes)
            else:
                nodes.append(node)

        return Wikicode(SmartList(nodes))

    def _substitute(self, wikitext, arguments=None, level=0):
        """
        """
        if not arguments:
            arguments = {}

        tree = parse(wikitext)

        nodes = deque()

        for node in tree.nodes:
            action = self._action_subst.get(type(node))
            if action:
                action(node, arguments=arguments, level=level, parent=nodes)
            else:
                nodes.append(node)

        return Wikicode(SmartList(nodes))

    def _expand_comment(self, comment, arguments, level, parent):
        pass

    def _expand_heading(self, heading, arguments, level, parent, fn=None):
        expand = fn or self._expand

        title = expand(heading.title, arguments, level)
        parent.append(Heading(title, heading.level))

    def _expand_wikilink(self, link, arguments, level, parent, fn=None):
        """
        """
        expand = fn or self._expand

        title = expand(link.title, arguments, level)
        text = (expand(link.text, arguments, level)
                if link.text is not None else None)

        parent.append(Wikilink(title, text))

    def _expand_argument(self, arg, arguments, level, parent, fn=None):
        """
        """
        expand = fn or self._expand

        name = expand(arg.name, arguments, level)
        key = p3_str(name)

        replacement = arguments.get(key, arg.default)

        if replacement is not None:
            _append(parent, expand(replacement, arguments, level))
        else:
            parent.append(Text(p3_str(arg)))

    def _expand_template(self, tpl, arguments, level, parent, mode=_PARSER_FUNCTION_MODE):
        """
        return True on success, False if no expansion is done at this level
        """
        level += 1
        assert level < self.MAX_RECURSION, "max recursion exceeded"

        # pick the proper expansion mode
        f_expand = self._expand
        if mode == _SUBST_MODE:
            f_expand = self._substitute

        tl_name = f_expand(tpl.name, arguments, level)

        # try to expand as a parser function
        pf = PF.as_parser_function(tl_name, tpl.params)
        if pf is not None:
            exp_pf = self._expand_parser_function(pf, arguments, level, fn=f_expand)
            if exp_pf is not None:
                _append(parent, exp_pf)
                return True
            else:
                _append(parent, PF.as_template(pf))
                return False

        # look for template
        key = strip(tl_name)
        expanded = None
        tpl_body = None
        #tpl_expanded = None
        # if the template is not parameterized, look for previous expansion
        if not tpl.params:
            expanded = self._cache_post.get(key)
        try:
            if expanded is None:
                if mode != _INVOKE_MODE:
                    call_tl = self.templates.callable_templates.get(key)
                else:
                    if key not in self.templates.callable_templates:
                        raise NotImplementedError("#invoke:" + key)
                    call_tl = self.templates.callable_templates[key]
                try:
                    # first look for template
                    if not call_tl:
                        tpl_body = self._cache_pre.get(
                            key,
                            self.templates.parse(key))
                        # cache the parsed body
                        self._cache_pre[key] = tpl_body
                except KeyError:
                    # otherwise look for magic word
                    if tpl.params:
                        raise
                    expanded = self.magic_words(key)

                # if not expanded, it is a call or a body
                if not expanded:
                    params = dict(_expand_template_kv(prm, arguments, level, f_expand)
                                  for prm in tpl.params)
                    if call_tl:
                        fn = partial(f_expand, level=level)
                        expanded = call_tl(
                            params,
                            fn,  # expander
                            self.context,  # context
                            arguments  # frame
                        )
                    else:
                        expanded = f_expand(tpl_body, params, level)

                # cache the expansion
                if not tpl.params:
                    self._cache_post[key] = expanded

            _append(parent, expanded)
            return True
        except KeyError as e:
            print("template or magic word not found: '%s'" % repr(e),
                  p3_str(tpl), file=sys.stderr)
            # try normalized name
            if self.context.site_context():
                canon = self.context.site_context().clean_title(key, external=True)
                if canon != key:
                    print("trying canonical title: '%s'" % canon, file=sys.stderr)
                    tpl.name = str2wikicode(canon)
                    return self._expand_template(
                        tpl,
                        arguments,
                        level - 1,
                        parent,
                        mode
                    )
            parent.append(tpl)
            return False

    def _expand_parser_function(self, pf, arguments, level, fn=None):
        """
        """
        expand = fn or self._expand

        pf_name = strip(pf.name)

        special_mode = _PF_MODE.get(pf_name, _PARSER_FUNCTION_MODE)

        if not special_mode and self.context.site_context():
            "{{Template:foobar|bla|bla}}"
            is_template = self.context.site_context().namespace_code(pf_name) == 10
            if is_template:
                special_mode = _SUBST_MODE

        if special_mode:
            # substitute or invoke instead of expand
            if pf.params:
                tpl_name = expand(pf.params[0].value)
                pf.params[0].value = tpl_name
            else:
                tpl_name = mw.parse(None)
            tpl = Template(tpl_name, reindex_params(pf.params[1:], -1))
            parent = SmartList()
            ok = self._expand_template(
                tpl,
                arguments,
                level,
                parent,
                mode=special_mode
            )
            if ok:
                return Wikicode(parent)
            else:
                return None

        # parameters will be expanded lazily
        def param_expander(parameter):
            if isinstance(parameter, Parameter):
                k, v = _expand_template_par(parameter, arguments, level, expand)
                return Parameter(k, v, showkey=parameter.showkey)
            else:
                return expand(parameter, arguments, level)

        try:
            return self.parser_function(pf_name, pf, param_expander)
        except KeyError as e:
            print("parser function not found: '%s'" % repr(e), file=sys.stderr)

        return None

    def _expand_tag(self, tag, arguments, level, parent, fn=None):
        """
        """
        expand = fn or self._expand

        tag_name = strip(tag.tag).lower()
        if tag_name == "includeonly":
            if tag.contents is not None:
                _append(parent, expand(tag.contents, arguments, level))
            return

        contents = (expand(tag.contents, arguments, level)
                    if tag.contents is not None else None)

        attrs = [_expand_attribute(a, arguments, level, expand)
                 for a in tag.attributes]

        replacement = Tag(
            tag=tag.tag,
            contents=contents,
            attrs=attrs,
            wiki_markup=tag.wiki_markup,
            self_closing=tag.self_closing,
            invalid=tag.invalid,
            implicit=tag.implicit,
            padding=tag.padding,
            closing_tag=tag.closing_tag,
            wiki_style_separator=tag.wiki_style_separator,
            closing_wiki_markup=tag.closing_wiki_markup
        )
        parent.append(replacement)


def _expand_attribute(attr, arguments, level, fn):
    name = fn(attr.name, arguments, level)
    value = (fn(attr.value, arguments, level)
             if attr.value is not None else None)
    return Attribute(
        name,
        value=value,
        quotes=attr.quotes,
        pad_first=attr.pad_first,
        pad_before_eq=attr.pad_before_eq,
        pad_after_eq=attr.pad_after_eq,
        check_quotes=False
    )


def _expand_template_par(prm, arguments, level, fn):
    """
    """
    pr_name = prm.name
    pr_value = fn(prm.value, arguments, level)
    if prm.showkey:
        pr_name = fn(pr_name, arguments, level)
        pr_value = strip_code(pr_value)

    return pr_name, pr_value


def _expand_template_kv(*args, **kwargs):
    """
    """
    pr_name, pr_value = _expand_template_par(*args, **kwargs)

    return strip(pr_name), pr_value
