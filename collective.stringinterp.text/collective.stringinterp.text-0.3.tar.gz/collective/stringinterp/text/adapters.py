# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.component.interfaces import ComponentLookupError

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.BaseUnit import BaseUnit

from plone.stringinterp.interfaces import IStringSubstitution
from plone.stringinterp.adapters import BaseSubstitution

# trick for don't campture category when running i18ndude
from plone.stringinterp import _ as PMF
# plone domain is used
from collective.stringinterp.text import _
from collective.stringinterp.text.interfaces import ITextExtractor


class TextSubstitution(BaseSubstitution):
    """Full body text substitution"""

    implements(IStringSubstitution)

    category = PMF(u'All Content')
    description = _(u'Body text')

    def safe_call(self):
        try:
            adapter = ITextExtractor(self.context)
        except ComponentLookupError:
            return None
        if adapter.text:
            return "\n".join([l.strip() for l in adapter.text.splitlines()])
        return ""


class IndentedTextSubstitution(TextSubstitution):
    """Like full body text substitution aobve, but with indentation chars"""

    implements(IStringSubstitution)

    description = _(u'Body text (indented)')

    def safe_call(self):
        text = TextSubstitution.safe_call(self)
        if text:
            return "\n".join(["\t" + l for l in text.splitlines()])


class ATTextExtractor(object):
    """Extract text field from ATCT contents"""

    implements(ITextExtractor)

    def __init__(self, context):
        self.context = context

    @property
    def text(self):
        context = self.context
        field = context.getField('text')
        if field:
            text = field.get(context)
            transforms = getToolByName(context, 'portal_transforms')
            stream = transforms.convertTo('text/plain',
                                          text,
                                          mimetype='text/html')
            return stream.getData().strip()


class PADiscussionTextExtractor(object):
    """Extract text field from plone.app.discussion comments"""

    implements(ITextExtractor)

    def __init__(self, context):
        self.context = context

    @property
    def text(self):
        context = self.context
        text = context.getText()
        transforms = getToolByName(context, 'portal_transforms')
        stream = transforms.convertTo('text/plain', text, mimetype='text/html')
        return stream.getData().strip()


class DexterityTextExtractor(object):
    """Try to extract text from Dexterity contents
    """

    implements(ITextExtractor)

    def __init__(self, context):
        self.context = context

    @property
    def text(self):
        context = self.context
        text = getattr(context, 'text', '')
        if isinstance(text, basestring):
            text = text.decode('utf-8')
        else:
            text = getattr(context.text, 'output', '')
        transforms = getToolByName(context, 'portal_transforms')
        stream = transforms.convertTo('text/plain', text, mimetype='text/html')
        return stream.getData().strip()


class GeneralTextExtractor(object):
    """Try to extract text from something (AKA: there is a "text" attribute?)
    """

    implements(ITextExtractor)

    def __init__(self, context):
        self.context = context

    @property
    def text(self):
        context = self.context
        text = getattr(context, 'text', '')
        if isinstance(text, basestring):
            text = text.decode('utf-8')
        elif isinstance(text, BaseUnit):
            # Ploneboard use this mess
            text = str(text).decode('utf-8')
        else:
            return ''
        transforms = getToolByName(context, 'portal_transforms')
        stream = transforms.convertTo('text/plain', text, mimetype='text/html')
        return stream.getData().strip()
