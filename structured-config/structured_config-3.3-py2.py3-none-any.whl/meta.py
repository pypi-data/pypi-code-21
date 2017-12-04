class _ConstructionOrderDict(dict):
    """Track field order and ensure field names are not reused.

    TypeStructure will use the names found in self.__field_names__ to translate
    to indices.
    """

    def __init__(self, *args, **kwds):
        self.__field_names__ = []
        super(_ConstructionOrderDict, self).__init__(*args, **kwds)

    def __setitem__(self, key, value):
        """Records anything not dundered or not a descriptor.

        If a field name is used twice, an error is raised.

        Single underscore (sunder) names are reserved.
        """
        if key in self.__field_names__:
            # overwriting a field?
            raise TypeError('Attempted to reuse field name: %r' % key)
        elif key[:2] == key[-2:] == '__':
            pass
        elif not (hasattr(value, '__get__') or  # Check not a descriptor
                  hasattr(value, '__set__') or
                  hasattr(value, '__delete__')):
            self.__field_names__.append(key)
        super(_ConstructionOrderDict, self).__setitem__(key, value)


class TypeStructure(type):
    @classmethod
    def __prepare__(mcs, cls, bases, *args, **kwargs):
        return _ConstructionOrderDict()

    def __init__(cls, name, bases, dct):
        cls.__field_names__ = dct.__field_names__
        super(TypeStructure, cls).__init__(name, bases, dct)