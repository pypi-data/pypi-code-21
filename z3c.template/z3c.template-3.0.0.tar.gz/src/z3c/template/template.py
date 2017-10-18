##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Implementation of templates.
"""

from zope import component
from zope.pagetemplate.interfaces import IPageTemplate
from zope.pagetemplate.pagetemplate import PageTemplate
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from z3c.template import interfaces


class Macro(object):
    # XXX: We can't use Zope's `TALInterpreter` class directly
    # because it (obviously) only supports the Zope page template
    # implementation. As a workaround or trick we use a wrapper
    # template.

    wrapper = PageTemplate()
    wrapper.write(
        '<metal:main use-macro="python: options[\'macro\']" />'
        )

    def __init__(self, template, name, view, request, contentType):
        self.macro = template.macros[name]
        self.contentType = contentType
        self.view = view
        self.request = request

    def __call__(self, **kwargs):
        kwargs['macro'] = self.macro
        kwargs.setdefault('view', self.view)
        kwargs.setdefault('request', self.request)
        result = self.wrapper(**kwargs)

        if not self.request.response.getHeader("Content-Type"):
            self.request.response.setHeader(
                "Content-Type", self.contentType)

        return result


class TemplateFactory(object):
    """Template factory."""

    template = None

    def __init__(self, filename, contentType, macro=None):
        self.contentType = contentType
        self.template = ViewPageTemplateFile(
            filename, content_type=contentType)
        self.macro = macro

    def __call__(self, view, request, context=None):
        if self.macro is None:
            return self.template
        return Macro(
            self.template, self.macro, view, request, self.contentType)


class BoundViewTemplate(object):
    __self__ = None
    __func__ = None

    def __init__(self, pt, ob):
        object.__setattr__(self, '__func__', pt)
        object.__setattr__(self, '__self__', ob)

    im_self = property(lambda self: self.__self__)
    im_func = property(lambda self: self.__func__)


    def __call__(self, *args, **kw):
        if self.__self__ is None:
            im_self, args = args[0], args[1:]
        else:
            im_self = self.__self__
        return self.__func__(im_self, *args, **kw)

    def __setattr__(self, name, v):
        raise AttributeError("Can't set attribute", name)

    def __repr__(self):
        return "<BoundViewTemplate of %r>" % self.__self__


class ViewTemplate(object):
    def __init__(self, provides=IPageTemplate, name=u''):
        self.provides = provides
        self.name = name

    def __call__(self, instance, *args, **keywords):
        template = component.queryMultiAdapter(
            (instance, instance.request, instance.context),
            self.provides, name=self.name)
        if template is None:
            template = component.getMultiAdapter(
                    (instance, instance.request),
                    self.provides, name=self.name)
        return template(instance, *args, **keywords)

    def __get__(self, instance, type):
        return BoundViewTemplate(self, instance)

getViewTemplate = ViewTemplate


class GetPageTemplate(ViewTemplate):

    def __init__(self, name=u''):
        self.provides = interfaces.IContentTemplate
        self.name = name

getPageTemplate = GetPageTemplate


class GetLayoutTemplate(ViewTemplate):

    def __init__(self, name=u''):
        self.provides = interfaces.ILayoutTemplate
        self.name = name

getLayoutTemplate = GetLayoutTemplate
