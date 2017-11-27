from ..error import SirenNotUriError
from enum import Enum
import re


class SirenRelValue:
    pass


_uri_pattern = re.compile(
    """^https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_+.~#?&//=]*)$""")


class SirenUriRelValue(SirenRelValue):
    def __init__(self, uri):
        if _uri_pattern.match(uri) is None:
            raise SirenNotUriError("Invalid Media Type [%s]", type)
        self._uri = uri

    @property
    def data(self):
        return self._uri


class SirenPredefRelValue(SirenRelValue, Enum):
    ABOUT = "about"
    ALTERNATE = "alternate"
    APPENDIX = "appendix"
    ARCHIVES = "archives"
    AUTHOR = "author"
    BLOCKED_BY = "blocked-by"
    BOOKMARK = "bookmark"
    CANONICAL = "canonical"
    CHAPTER = "chapter"
    COLLECTION = "collection"
    CONTENTS = "contents"
    CONVERTED_FROM = "convertedFrom"
    COPYRIGHT = "copyright"
    CREATE_FORM = "create-form"
    CURRENT = "current"
    DERIVED_FROM = "derivedfrom"
    DESCRIBED_BY = "describedby"
    DESCRIBES = "describes"
    DISCLOSURE = "disclosure"
    DNS_PREFETCH = "dns-prefetch"
    DUPLICATE = "duplicate"
    EDIT = "edit"
    EDIT_FORM = "edit-form"
    EDIT_MEDIA = "edit-media"
    ENCLOSURE = "enclosure"
    FIRST = "first"
    GLOSSARY = "glossary"
    HELP = "help"
    HOSTS = "hosts"
    HUB = "hub"
    ICON = "icon"
    INDEX = "index"
    ITEM = "item"
    LAST = "last"
    LATEST_VERSION = "latest-version"
    LICENSE = "license"
    LRDD = "lrdd"
    MEMENTO = "memento"
    MONITOR = "monitor"
    MONITOR_GROUP = "monitor-group"
    NEXT = "next"
    NEXT_ARCHIVE = "next-archive"
    NOFOLLOW = "nofollow"
    NOREFERRER = "noreferrer"
    ORIGINAL = "original"
    PAYMENT = "payment"
    PINGBACK ="pingback"
    PRECONNECT = "preconnect"
    PREDECESSOR_VERSION = "predecessor-version"
    PREFETCH = "prefetch"
    PRELOAD = "preload"
    PRERENDER = "prerender"
    PREV = "prev"
    PREVIEW = "preview"
    PREVIOUS = "previous"
    PREV_ARCHIVE = "prev-archive"
    PRIVACY_POLICY = "privacy-policy"
    PROFILE = "profile"
    RELATED = "related"
    RESTCONF ="restconf"
    REPLIES = "replies"
    SEARCH = "search"
    SECTION = "section"
    SELF = "self"
    SERVICE = "service"
    START = "start"
    STYLESHEET = "stylesheet"
    SUBSECTION = "subsection"
    SUCCESSOR_VERSION = "successor-version"
    TAG = "tag"
    TERMS_OF_SERVICE = "terms-of-service"
    TIMEGATE = "timegate"
    TIMEMAP = "timemap"
    TYPE = "type"
    UP = "up"
    VERSION_HISTORY = "version-history"
    VIA = "via"
    WEBMENTION = "webmention"
    WORKING_COPY = "working-copy"
    WORKING_COPY_OF = "working-copy-of"
