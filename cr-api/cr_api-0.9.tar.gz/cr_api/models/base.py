# -*- coding: utf-8 -*-

"""
Clash Royale models.
"""

from json import dumps, loads
from logging import getLogger

__timeformat__ = '%Y-%m-%dT%H:%M:%SZ'
__logs__ = getLogger(__package__)




class BaseModel(object):
    """Clash Royale base model."""

    def __init__(self, data=None, url=None):
        if url is not None:
            self._uniq = url
        self._data = data
        self._update_attributes(data)

    def _update_attributes(self, data):
        pass

    def __getattr__(self, attribute):
        """Proxy acess to stored JSON."""
        if attribute not in self._data:
            raise AttributeError(attribute)
        value = self._data.get(attribute)
        setattr(self, attribute, value)
        return value

    def as_dict(self):
        """Return the attributes for this object as a dictionary.

        This is equivalent to calling:

            json.loads(obj.as_json())

        :returns: this object’s attributes seriaized as a dictionary
        :rtype: dict
        """
        return self._data

    def as_json(self):
        """Return the json data for this object.

        This is equivalent to calling:

            json.dumps(obj.as_dict())

        :returns: this object’s attributes as a JSON string
        :rtype: str
        """
        return dumps(self._data)

    @classmethod
    def _get_attribute(cls, data, attribute, fallback=None):
        """Return the attribute from the JSON data.

        :param dict data: dictionary used to put together the model
        :param str attribute: key of the attribute
        :param any fallback: return value if original return value is falsy
        :returns: value paried with key in dict, fallback
        """
        if data is None or not isinstance(data, dict):
            return None
        result = data.get(attribute)
        if result is None:
            return fallback
        return result

    @classmethod
    def __class_attribute(cls, data, attribute, cl, *args, **kwargs):
        """Return the attribute from the JSON data and instantiate the class.

        "param dict data: dictionary used to put together the model or None
        "param str attribute: key of the attribute
        :param class cl: class that will be instantiated
        :returns: instantiated class or None
        :rtype: object or None
        """
        value = cls._get_attribute(data, attribute)
        if value:
            return cl(
                value,
                *args,
                **kwargs
            )
        return value

    def __repr__(self):
        repr_string = self._repr()
        return repr_string

    @classmethod
    def from_dict(cls, json_dict):
        """Return an instanc of this class formed from ``json_dict``."""
        return cls(json_dict)

    @classmethod
    def from_json(cls, json):
        """Return an instane of this class formed from ``json``."""
        return cls(loads(json))

    def __eq__(self, other):
        return self._uniq == other._uniq

    def __ne__(self, other):
        return self._uniq != other._uniq

    def _repr(self):
        return "{}({})".format(self.__class__, self.__dict__)



