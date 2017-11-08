""" Widget
"""
from Products.Archetypes.atapi import StringWidget
from zope.interface import implements
from zope.app.form.browser.interfaces import IBrowserWidget
from zope.app.form.interfaces import IInputWidget
from zope.schema import Field
from zope.schema.interfaces import IField
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from eea.geotags.field.location import GeotagsFieldMixin

class GeotagsWidget(StringWidget):
    """ Geotags
    """
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro': "eea.geotags",
        'dialog': '@@eea.geotags.dialog',
        'sidebar': '@@eea.geotags.sidebar',
        'basket': '@@eea.geotags.basket',
        'json': '@@eea.geotags.json',
        'suggestions': '@@eea.geotags.suggestions',
    })

###
# Formlib widget
######

class IGeotagSingleField(IField):
    """ The field interface
    """

class GeotagMixinField(Field, GeotagsFieldMixin):
    """ Geotag Mixin Field
    """

    def set(self, instance, value, **kwargs):
        """ Set
        """
        self.setJSON(instance.context, value, **kwargs)

class GeotagSingleField(GeotagMixinField):
    """ Geotag Single Field
    """
    implements(IGeotagSingleField)

    @property
    def multiline(self):
        """ Multiline
        """
        return False

class IGeotagMultiField(IField):
    """ The field interface
    """

class GeotagMultiField(GeotagMixinField):
    """ Geotag Multi Field
    """
    implements(IGeotagMultiField)

    @property
    def multiline(self):
        """ Multiline
        """
        return True

class FormlibGeotagWidget(object):
    """ Formlib Geotag Widget
    """
    implements(IBrowserWidget, IInputWidget)
    template = ViewPageTemplateFile("location.pt")

    # See zope.app.form.interfaces.IInputWidget
    name = None
    label = property(lambda self: self.context.title)
    hint = property(lambda self: self.context.description)
    visible = True
    required = property(lambda self: self.context.required)

    _prefix = "form."
    _value = None
    _error = None

    dialog = '@@eea.geotags.dialog'
    sidebar = '@@eea.geotags.sidebar'
    basket = '@@eea.geotags.basket'
    json = '@@eea.geotags.json'
    suggestions = '@@eea.geotags.suggestions'

    def __init__(self, field, request):
        self.context = field
        self.request = request
        self.name = self._prefix + field.__name__

    def setPrefix(self, prefix):
        """ See zope.app.form.interfaces.IWidget
        """
        # Set the prefix locally
        if not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
        self.name = prefix + self.context.__name__

    def setRenderedValue(self, value):
        """ Set rendered value
        """
        pass

    def hasInput(self):
        """ Has input
        """
        val = self.request.form.get('location')
        if val and val.strip():
            return True

        return False

    def error(self):
        """ See zope.app.form.browser.interfaces.IBrowserWidget
        """
        if self._error:
            return "Need valid input"

    def getInputValue(self):
        """ Get input value
        """
        return self.request.form['location']

    def applyChanges(self, content):
        """ See zope.app.form.interfaces.IInputWidget
        """
        field = self.context
        new_value = self.getInputValue()
        old_value = field.query(content, self)
        # The selection has not changed
        if new_value == old_value:
            return False
        field.set(content, new_value)
        return True

    def __call__(self):
        return self.template()
