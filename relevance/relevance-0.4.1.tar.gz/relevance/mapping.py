"""
Relevance mapping module.

This module provides the interface for defining schema mappings.
"""

import copy
import typing


class Field(object):
    """
    Mapping field class.

    This class provides a generic interface for mapping a field name to a Python
    data type as engine agnostic.
    """
    def __init__(self, name: str, data_type: type, stored: bool=True, **options):
        """
        Initialize the field.

        :param name: the name of the field.
        :param data_type: the Python data type class.
        :param stored: whether to store the value of the field or just index it.
        :param options: additional options to store for the mapping.
        """
        self.name = name
        self.data_type = data_type
        self.stored = stored
        self.options = options

    def to_dict(self) -> typing.Dict[str, object]:
        """
        Get the field as a dictionary.
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
        Overload operator for readable representation.
        """
        return '{0}:{1}'.format(self.name, self.data_type.__name__)


class Mapping(object):
    """
    Mapping class.

    This class provides a generic interface for defining engine agnostic mappings.
    Mapping objects define a list of fields.
    """
    def __init__(self, *fields):
        """
        Initialize the mapping.

        :param fields: the list of field objects for the mapping.
        """
        self.fields = list(fields)

    def add(self, field: Field) -> 'Mapping':
        """
        Add a field to the mapping.

        :param field: the field object to add.
        :returns: the new updated mapping object.
        """
        self = copy.deepcopy(self)
        self.fields.append(field)
        return self

    def to_dict(self) -> typing.Dict[str, dict]:
        """
        Get the mapping as a dictionary.
        """
        result = {}
        for x in self.fields:
            result[x.name] = x.to_dict()
        return result

    def __getitem__(self, name: str) -> Field:
        """
        Get a field by its name.

        :param name: the name of the field.
        :returns: the field object.
        :raises: KeyError: when the field does not exist.
        """
        for x in self.fields:
            if x.name == name:
                return x
        raise KeyError(name)

    def __contains__(self, name: str) -> bool:
        """
        Check if a field is part of the mapping.

        :param name: the field name.
        :returns: True if it exists, False otherwise.
        """
        for x in self.fields:
            if x.name == name:
                return True
        return False

    def __iter__(self) -> typing.Iterable:
        """
        Iterate over all the fields.

        :returns: an iterator object.
        """
        return iter(self.fields)

    def __repr__(self) -> str:
        """
        Overload operator for readable representation.
        """
        return repr(list(self.fields))


class ObjectField(Field):
    """
    Object field class.

    This class provides the interface for mapping an object field. Object fields
    are fields that have nested mappings in them.
    """
    def __init__(self, name: str, mapping: Mapping, *args, **kwargs):
        """
        Initialize the field.

        :param name: the name of the field.
        :param mapping: the mapping object for the field.
        """
        super().__init__(name, dict, *args, **kwargs)
        self.mapping = mapping

    def to_dict(self) -> typing.Dict[str, object]:
        """
        Get the field as a dictionary.
        """
        data = super().to_dict()
        del data['data_type']
        data['fields'] = self.mapping.to_dict()
        return data
