import re
from enum import Enum
from typing import Dict, List

from ..entities.rel import SirenRelValue
from ..entities.media_type import SirenMediaType
from ..error import *
from ..renderer import RendererMixin
from ..renderer import SirenBase


class Method(Enum):
    DELETE = 'DELETE'
    GET = 'GET'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'

class SirenLink(RendererMixin, SirenBase):
    def __init__(self, rel: List[SirenRelValue], href: str, title: str=None, type: SirenMediaType=None, classes: List[str]=None):
        self._rel = rel
        self._href = href
        self._title = title
        self._type = type
        self._class = classes


class FieldType(Enum):
    HIDDEN = "hidden"
    TEXT = "text"
    SEARCH = "search"
    TEL = "tel"
    URL = "url"
    EMAIL = "email"
    PASSWORD = "password"
    DATETIME = "datetime"
    DATE = "date"
    MONTH = "month"
    WEEK = "week"
    TIME = "time"
    DATETIME_LOCAL = "datetime-local"
    NUMBER = "number"
    RANGE = "range"
    COLOR = "color"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"




class Field(RendererMixin, SirenBase):
    def __init__(self, name: str, title: str=None, value=None, type: FieldType=FieldType.TEXT):
        self._name = name
        self._title = title
        self._value = value
        self._type = type


class SirenAction(RendererMixin, SirenBase):
    def __init__(self, name: str, href: str,
                 title: str=None, method: Method=Method.GET,
                 classes: List[str]=None, type: SirenMediaType=SirenMediaType('application/x-www-form-urlencoded'), fields: List[Field]=None):
        self._name = name
        self._href = href
        self._title = title
        self._method = method
        self._class = classes
        self._type = type
        self._fields = fields

class SirenEntity(RendererMixin, SirenBase):
    # class
    # title
    # properties
    # entities
    # actions
    # links
    # _class: List[str] = []
    # _title: str = ''
    # _properties: Dict[str, str] = {}
    # _entities: List[object] = []

    def __init__(self,
                 classes: List[str],
                 title: str=None,
                 properties: Dict[str, object]=None,
                 entities: List[object]=None,
                 links: List[SirenLink]=None,
                 actions: List[SirenAction] = None):
        self._class = classes
        self._title = title
        self.set_properties(properties)
        self.set_entities(entities)
        self._links = links
        self._actions = actions

    def get_class(self):
        return self._class

    def get_properties(self):
        return self._properties

    def set_properties(self, properties):
        if properties is not None and type(properties) != dict:
            raise SirenEntityError("Properties are of type {}, dictionary expected!", type(properties))

        self._properties = properties

    def add_property(self, name, value):
        self._properties[name] = value

    def remove_property(self, name):
        del self._properties[name]

    def set_entities(self, entities):
        self._entities = entities


class SirenSubEntity(SirenEntity, RendererMixin):
    pass

class EmbeddedLinkSubEntity(SirenSubEntity, RendererMixin):
    pass


class EmbeddedRepresentationSubEntity(SirenSubEntity, RendererMixin):
    def __init__(self,
                 classes: List[str],
                 rel: SirenRelValue,
                 title: str = None,
                 properties: Dict[str, object] = None,
                 entities: List[SirenSubEntity] = None,
                 links: List[SirenLink] = None,
                 actions:List[SirenAction] = None):
        SirenEntity.__init__(self, classes, title, properties, entities, links, actions)
        self._rel = rel