from typing import Dict, List
from enum import Enum
import re
from .renderer import SirenBase
from .renderer import RendererMixin

class SirenError(Exception):
    pass


class SirenEntityError(SirenError):
    pass


class SirenMediaTypeError(SirenError):
    pass


_media_type_pattern = re.compile("^(application|audio|image|message|model|multipart|text|video)\\/([A-Z]|[a-z]|[0-9]|[\\!\\#\\$\\&\\.\\+\\-\\^\\_]){1,127}(; ?(([\\!\\#\\$\\%\\&\\'\\(\\)\\*\\+-\\.\\/]|[0-9]|[A-Z]|[\\^\\_\\`\\]\\|]|[a-z]|[\\|\\~])+)+=((([\\!\\#\\$\\%\\&\\'\\(\\)\\*\\+-\\.\\/]|[0-9]|[A-Z]|[\\^\\_\\`\\]\\|]|[a-z]|[\\|\\~])+)|\"([\\!\\#\\$\\%\\&\\.\\(\\)\\*\\+\\,\\-\\.\\/]|[0-9]|[\\:\\;\\<\\=\\>\\?\\@]|[A-Z]|[\\[\\\\\\]\\^\\_\\`]|[a-z]|[\\{\\|\\}\\~])+\"))*$")





class MediaType(RendererMixin):
    def __init__(self, type):
        if _media_type_pattern.match(type) is None:
            raise SirenMediaTypeError("Invalid Media Type [%s]", type)
        else:
            self._type = type

    def get_type(self):
        return self._type

class RelValue(Enum):
    ABOUT = "about"
    #ALTERNATE = "alternate",
    APPENDIX = "appendix"
    #"archives",
    AUTHOR = "author"
    #"blocked-by",
    #"bookmark",
    #"canonical",
    #"chapter",
    COLLECTION = "collection"
    CONTENTS = "contents"
    #"convertedFrom",
    #"copyright",
    #"create-form",
    #"current",
    DERIVED_FROM = "derivedfrom"
    DESCRIBED_BY = "describedby"
    DESCRIBES = "describes"
    #"disclosure",
    #"dns-prefetch",
    #"duplicate",
    EDIT = "edit"
    EDIT_FORM = "edit-form"
    #"edit-media",
    #"enclosure",
    FIRST = "first"
    GLOSSARY = "glossary"
    HELP = "help"
    #"hosts",
    #"hub",
    #"icon",
    INDEX = "index"
    ITEM = "item"
    LAST = "last"
    LATEST_VERSION = "latest-version"
    LICENSE = "license"
    #"lrdd",
    #"memento",
    #"monitor",
    #"monitor-group",
    NEXT = "next"
    #"next-archive",
    #"nofollow",
    #"noreferrer",
    #"original",
    #"payment",
    #"pingback",
    #"preconnect",
    #"predecessor-version",
    #"prefetch",
    #"preload",
    #"prerender",
    PREV = "prev"
    PREVIEW = "preview"
    PREVIOUS = "previous"
    #"prev-archive",
    #"privacy-policy",
    PROFILE = "profile"
    RELATED = "related"
    #"restconf",
    #"replies",
    SEARCH = "search"
    #"section",
    SELF = "self"
    #"service",
    #"start",
    #"stylesheet",
    #"subsection",
    #"successor-version",
    #"tag",
    #"terms-of-service",
    #"timegate",
    #"timemap",
    #"type",
    UP = "up"
    #"version-history",
    #"via",
    #"webmention",
    #"working-copy",
    #"working-copy-of"


class Method(Enum):
    DELETE = 'DELETE'
    GET = 'GET'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'

class SirenLink(RendererMixin, SirenBase):
    def __init__(self, rel: List[RelValue], href: str, title: str=None, type: MediaType=None, classes: List[str]=None):
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
                 classes: List[str]=None, type: MediaType=MediaType('application/x-www-form-urlencoded'), fields: List[Field]=None):
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
                 rel: RelValue,
                 title: str = None,
                 properties: Dict[str, object] = None,
                 entities: List[SirenSubEntity] = None,
                 links: List[SirenLink] = None,
                 actions:List[SirenAction] = None):
        SirenEntity.__init__(self, classes, title, properties, entities, links, actions)
        self._rel = rel