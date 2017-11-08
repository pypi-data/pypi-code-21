""" Custom zope schema
"""
from zope.interface import implements
from zope.formlib.textwidgets import TextWidget
from zope.formlib.widget import renderElement
from zope.formlib.interfaces import ConversionError
from zope.schema.interfaces import IList
from zope.schema.interfaces import ITuple
from zope import schema
from plone.app.form.widgets import ListSequenceWidget
from eea.alchemy.config import EEAMessageFactory as _

class ITable(IList):
    """ Interface for Table field
    """

class ITableRow(ITuple):
    """ Interface for TableRow field
    """

class Table(schema.List):
    """ Table field
    """
    implements(ITable)

class TableRow(schema.Tuple):
    """ Pair of values
    """
    cells = 2
    delimiter = u','
    implements(ITableRow)

class TableRowWidget(TextWidget):
    """ Widget
    """
    def __call__(self):
        res = u''
        value = self._getFormValue()
        if value is None or value == self.context.missing_value:
            value = []

        if isinstance(value, (str, unicode)):
            value = value.split(self.context.delimiter)

        for cell in range(0, self.context.cells):
            kwargs = {'type': self.type,
                      'name': self.name,
                      'id': self.name + '%s' % cell,
                      'value': value[cell] if len(value) > cell else u'',
                      'cssClass': self.cssClass,
                      'style': self.style,
                      'size': self.displayWidth,
                      'extra': self.extra
                      }
            if self.displayMaxWidth:
                kwargs['maxlength'] = self.displayMaxWidth

            if cell:
                res += u'&nbsp; &rarr; &nbsp;'
            res += renderElement(self.tag, **kwargs)
        return res

    def _toFieldValue(self, input):
        """ Convert form value to field value
        """
        if self.convert_missing_value and input == self._missing:
            value = self.context.missing_value
        else:
            if isinstance(input, (str, unicode)):
                input = [input, '']
            elif isinstance(input, list):
                input = tuple(input)

            try:
                value = tuple(str(x) for x in input)
            except ValueError, v:
                raise ConversionError(_("Invalid text data"), v)
        return value

class TableWidget(ListSequenceWidget):
    """ Custom widget for table
    """
    def _getPresenceMarker(self, count=0):
        """ Safely get presence marker
        """
        try:
            return super(TableWidget, self)._getPresenceMarker(count=count)
        except Exception:
            orig = ' originalValue="0"'
            return ('<input type="hidden" name="%s.count" value="%d"%s />' % (
                self.name, count, orig))
