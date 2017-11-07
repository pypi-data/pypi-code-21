# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute

class ITextExtractor(Interface):
    """An object that can extract text field data from the context"""

    text = Attribute('''text from the content''')
