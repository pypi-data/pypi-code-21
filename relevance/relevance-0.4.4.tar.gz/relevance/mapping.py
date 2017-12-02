"""
The mapping module provides an abstract interface for managing index schema mappings across
different search engine implementations.
"""

# pylint: disable=too-few-public-methods

import typing


class Field(object):
    """
    This is the base class used to represent a mapped field.
    """
    def __init__(self, name: str, data_type: type, stored: bool = True, **options) -> None:
        """
        :param name: the name of the field in the index.
        :param data_type: the data type for the field. Python data types (e.g.:
            :class:`str`, :class:`int`, etc.) should be supplied here.
        :param stored: a flag determining if the field should only be indexed or its
            value stored as well. Some engine implementations may ignore this flag.
        :param options: additional options to store for the mapping, typically engine
            specific, such as unsigned flags, maximum length, etc.
        """
        self.name = name
        self.data_type = data_type
        self.stored = stored
        self.options = options

    def to_dict(self) -> typing.Dict[str, object]:
        """
        Obtain the field mapping as a dictionary object.

        :return: a dictionary containing the field information.
        """
        data_type = '{0}.{1}'.format(
            self.data_type.__module__,
            self.data_type.__name__,
        )

        return {
            'name': self.name,
            'data_type': data_type,
            'stored': self.stored,
            'options': self.options,
        }

    def __repr__(self) -> str:
        """
        Implementation of the :func:`repr` function.
        """
        return '{0}:{1}'.format(self.name, self.data_type.__name__)


class Mapping(object):
    """
    This class is used to represent an index mapping, that is, a collection of
    fields that a particular schema uses.
    """
    def __init__(self, *fields):
        """
        :param fields: the list of field objects in the mapping.
        """
        self.fields = list(fields)

    def add(self, field: Field):
        """
        Add a field to the mapping.

        :param field: the field object to add.
        """
        self.fields.append(field)

    def to_dict(self) -> typing.Dict[str, dict]:
        """
        Obtain the mapping as a dictionary.

        This method also calls the :meth:`Field.to_dict` method on each field.

        :return: a dictionary object containing the mapping information.
        """
        result = {}
        for field in self.fields:
            result[field.name] = field.to_dict()
        return result

    def __getitem__(self, name: str) -> Field:
        """
        Get a field by its name.

        :param name: the name of the field.
        :return: the field object.
        :raises: :class:`FieldNotFoundError`: when the requested field does not exist.
        """
        for field in self.fields:
            if field.name == name:
                return field
        raise FieldNotFoundError(name)

    def __contains__(self, name: str) -> bool:
        """
        Check if a field is part of the mapping.

        :param name: the field name.
        :return: True if it exists, False otherwise.
        """
        for field in self.fields:
            if field.name == name:
                return True
        return False

    def __iter__(self) -> typing.Iterable:
        """
        Iterate over all the fields.

        :return: an iterator object that iterates over all the mapping's field,
            in order.
        """
        return iter(self.fields)

    def __repr__(self) -> str:
        """
        Implementation of the :func:`repr` function.
        """
        return repr(list(self.fields))


class ObjectField(Field):
    """
    This class provides the interface for mapping an object field. Object fields
    are fields that have nested mappings in them.
    """
    def __init__(self, name: str, mapping: Mapping, *args, **kwargs) -> None:
        """
        :param name: the name of the field.
        :param mapping: the mapping object for the field, representing the field's
            sub-fields.
        """
        super().__init__(name, dict, *args, **kwargs)
        self.mapping = mapping

    def to_dict(self) -> typing.Dict[str, object]:
        """
        Implementation of :meth:`Field.to_dict`.
        """
        data = super().to_dict()
        del data['data_type']
        data['fields'] = self.mapping.to_dict()
        return data


class FieldNotFoundError(NameError):
    """
    This exception class is raised when trying to get a field that does not exist in a
    specific mapping.
    """
    pass
