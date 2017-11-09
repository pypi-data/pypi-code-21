from .variable import Variable

class FieldAncillary(Variable):
    '''A CF field ancillary construct.
'''

    @property
    def isfieldancillary(self):
        '''True, denoting that the variable is a field ancillary object.

.. versionadded:: 2.0

.. seealso:: `isauxiliary`, `isdimension`, `isdomainancillary`,
             `ismeasure`

:Examples:

>>> f.isfieldancillary
True

        '''
        return True
    #--- End: def

    def dump(self, display=True, omit=(), field=None, key=None,
             _level=0, _title=None):
        '''Return a string containing a full description of the field ancillary
object.

:Parameters:

    display: `bool`, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``f.dump()`` is equivalent to
        ``print f.dump(display=False)``.

:Returns:

    out: `None` or `str`
        A string containing the description.

:Examples:

        '''
        if _title is None:
            _title = 'Field Ancillary: ' + self.name(default='')

        return super(FieldAncillary, self).dump(
            display=display, omit=omit, field=field, key=key,
             _level=_level, _title=_title)

#        indent0 = '    ' * _level
#        indent1 = '    ' * (_level+1)
#
#        string = ['{0}Field ancillary: {1}'.format(indent0, self.name(default=''))]
#
#        if self._hasData:
#            if field is not None:
#                x = ['{0}({1})'.format(field.axis_name(axis), field.axis_size(axis))
#                     for axis in field.item_axes(key)]
#                string.append('{0}Data({1}) = {2}'.format(indent1, ', '.join(x), str(self.Data)))
#            else:
#                x = [str(s) for s in self.shape]
#                string.append('{0}Data({1}) = {2}'.format(indent1, ', '.join(x), str(self.Data)))
#        #--- End: if
#
#        if self._simple_properties():
#            string.append(self._dump_simple_properties(_level=_level+1))
#          
#        string = '\n'.join(string)
#       
#        if display:
#            print string
#        else:
#            return string
    #--- End: def

#--- End: class
