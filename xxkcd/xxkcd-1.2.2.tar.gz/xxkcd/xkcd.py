# coding: utf-8

import sys
import weakref
import json
import datetime
import random
import functools
import posixpath
import multiprocessing

from objecttools import ThreadedCachedProperty

from xxkcd._util import (
    urlopen, reload, unescape, map, str_is_bytes, make_mapping_proxy,
    range, short, dead_weaklink, coerce_
)
from xxkcd import constants

__all__ = ('xkcd',)

_404_mock = make_mapping_proxy({
    'month': 4, 'num': 404, 'link': '', 'year': 2008, 'news': u'',
    'safe_title': u'404 not found', 'transcript': u'', 'alt': u'', 'img': '',
    'title': u'404 - Not Found', 'day': 1
})


def _decode(s):
    """
    Decodes the incorrect encoding used in the xkcd JSON api.

    All of the fields of xkcd comics that use non-ascii characters incorrectly
    encode binary UTF-8 as escaped UTF-8.

    For example, 'é' -> 0xC3 0xA9 -> '\\u00c3\\u00a9' in the JSON, which
    actually encodes 'Ã©'

    This is sometimes done multiple times, like in xkcd(124).

    :param str s: String to decode
    :return: Decoded string
    :rtype: Text
    """
    for _ in range(10):
        try:
            s = bytearray(map(ord, s)).decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            return unescape(s)
    return unescape(s)


def _load_one(comic):
    """
    Cache a comic so that it won't make HTTP requests and rely on the cache

    :param comic: The comic to cache. Consider using `xkcd.load_all()`
    :type comic: Union[int, xkcd, None]
    :return: None
    """
    xkcd(comic, True).json

# Python 2 and Python 3.6+ allow bytes JSON
_JSON_BYTES = sys.version_info < (3,) or sys.version_info >= (3, 6)

_MIMES = {
    '.png': 'image/png', '.jpg': 'image/jpeg', 'gif': 'image/gif',
    '.jpeg': 'image/jpeg'
}

___ = 'antigravity'
____ = sys.modules.get
_____ = None
______ = reload


class xkcd(object):
    """Interface with the xkcd JSON API"""
    __slots__ = ('_comic', '__weakref__', '__dict__')

    _cache = {}
    _keep_alive = {}

    def __new__(cls, comic=None, keep_alive=False):
        """
        Wrapper around the xkcd API for the comic

        :param Union[int, None, xkcd] comic: Number of the comic.
            -1 or `None` for the latest comic.
            -x means x comics before the latest comic.
        :param bool keep_alive: True to not delete the data requested until
            the `.delete()` method is called
        :return: The new xkcd object
        :rtype: xkcd
        :raises TypeError: Non-int given as comic
        """
        if isinstance(comic, cls):
            if keep_alive:
                cls._keep_alive[comic._comic] = comic
            return comic
        comic = coerce_(comic, cls.latest)
        self = cls._cache.get(comic, dead_weaklink)()
        if self is None:
            self = super(xkcd, cls).__new__(cls)
            self._comic = comic
            cls._cache[comic] = weakref.ref(self)
        if keep_alive:
            cls._keep_alive[comic] = self
        return self

    @property
    def comic(self):
        return self._comic

    @ThreadedCachedProperty
    def _raw_json(self):
        """Raw JSON with a possibly incorrect transcript and alt text"""
        if self._comic == 404:
            return make_mapping_proxy(_404_mock)
        if self._comic is None:
            url = constants.xkcd.json.latest
        else:
            url = constants.xkcd.json.for_comic(number=self._comic)
        with urlopen(url) as http:
            if _JSON_BYTES:
                return make_mapping_proxy(json.load(http))
            return make_mapping_proxy(json.loads(http.read().decode('utf-8')))

    _raw_json.can_delete = True

    @ThreadedCachedProperty
    def json(self):
        """
        JSON with the correct transcript and encoded properly.

        Note, that in Python 2, all of the `str` keys are `unicode`.

        Format::
        {
            'month': (the number of the month it was published. Possibly None.),
            'num': (int of the number of the comic),
            'link': (str of where the comic links to when clicked on, most commonly a larger version),
            'year': (the year it was published. Possibly None.),
            'news': (str of news that would be placed on the news ticker on the comic. Usually empty.),
            'safe_title': (str of url safe title),
            'transcript': (str of the transript. Possibly empty, usually for later comics),
            'alt': (str of the text that appears in the title attribute of the comic. Possibly empty.),
            'img': (str of the direct link to the image. Possibly empty, usually for interactive comics),
            'title': (str of the original title of the comic.),
            'day': (the number of the day it was published. Possibly None.)
        }

        Type stub::
        {
            'month': Optional[int], 'num': int, 'link': Text,
            'year': Optional[int], 'news': Text, 'safe_title': Text,
            'transcript': Text, 'alt': Text, 'img': Text, 'title': Text,
            'day' Optional[int]
        }
        """
        n = self._comic
        if n is None:
            pass
        # These comics messed up the transcripts.
        # They were interactive comics that didn't have a transcript that
        # pushed the transcripts for all other comics 1 or 2 ahead.
        elif n >= 1663:
            n += 3
        elif n >= 1608:
            n += 2
        if str_is_bytes:
            other_json = {}
            for key in self._raw_json:
                other_json[key.encode('ascii')] = self._raw_json[key]
        else:
            other_json = dict(self._raw_json)
        if n is not None and n < self.latest() - 3:
            other_json['transcript'] = _decode(xkcd(n)._raw_json['transcript'])
        else:
            other_json['transcript'] = _decode(other_json['transcript'])
        for text_key in ('alt', 'title', 'safe_title'):
            other_json[text_key] = _decode(other_json[text_key])
        for int_key in ('day', 'month', 'year'):
            if other_json[int_key]:
                other_json[int_key] = short(other_json[int_key])
            else:
                other_json[int_key] = None
        if other_json['img'] == constants.xkcd.images.blank:
            other_json['img'] = ''
        if str_is_bytes:
            other_json['img'] = other_json['img'].encode('ascii')
            other_json['link'] = other_json['link'].encode('ascii')
        return make_mapping_proxy(other_json)

    json.can_delete = True

    @property
    def month(self):
        return self.json['month']

    @property
    def link(self):
        return self.json['link']

    @property
    def year(self):
        return self.json['year']

    @property
    def news(self):
        return self.json['news']

    @property
    def safe_title(self):
        return self.json['safe_title']

    @property
    def transcript(self):
        return self.json['transcript']

    @property
    def alt(self):
        return self.json['alt']

    @property
    def img(self):
        return self.json['img']

    def read_image(self):
        """
        Read the raw image from the link and return the data.

        :raises ValueError: Comic doesn't have an image (e.g., it is xkcd(404), or it is interactive.)
        :return: Raw image data
        :rtype: bytes
        """
        if not self.img:
            raise ValueError('Comic {} does not have an image!'.format(self))
        with urlopen(self.img) as http:
            return http.read()

    def stream_image(self, file=None, chunk_size=2048):
        """
        Stream the raw image file from the link and write to file.

        :param file: File-like to write to, or None to return an iterator over the chunks
        :type file: Optional[BinaryIO]
        :param chunk_size: Size of chunks (or None for the whole file in a chunk. Consider `self.read_image()`.)
        :type chunk_size: Optional[int]
        :return: iterator or None
        :rtype: Optional[type(iter((lambda: None), None))]  # Optional[CallableIterator]
        """
        if not self.img:
            raise ValueError('Comic {} does not have an image!'.format(self))
        if file is None:
            with urlopen(self.img) as http:
                read = http.read
                if chunk_size is not None:
                    read = functools.partial(read, chunk_size)
                return iter(read, b'')
        for chunk in self.stream_image(chunk_size=chunk_size):
            file.write(chunk)

    @property
    def image_name(self):
        """Suggested name for the image file. None if no image."""
        if not self.img:
            return None
        return posixpath.basename(self.img)

    @property
    def image_ext(self):
        """File extension of image file. Usually '.png'. '' if no extension, None if no image."""
        image_name = self.image_name
        if image_name is None:
            return None
        return posixpath.splitext(self.image_name)[1]

    @property
    def image_mime(self):
        """
        Mime type of the image. Usually 'image/png'.
        'application/octet-stream' if not found, None if no image.
        """
        ext = self.image_ext
        if ext is None:
            return None
        if ext:
            return _MIMES.get(ext.lstrip('.').lower(), 'application/octet-stream')
        return 'application/octet-stream'

    @property
    def title(self):
        return self.json['title']

    @property
    def day(self):
        return self.json['day']

    @property
    def date(self):
        """
        :return: The day, month and year the comic was published.
        :rtype: datetime.date
        """
        return datetime.date(self.year, self.month, self.day)

    @classmethod
    def latest(cls):
        """
        :return: The number of the latest comic
        :rtype: int
        """
        return xkcd(keep_alive=True)._raw_json['num']

    @classmethod
    def random(cls):
        """
        :return: A random comic
        :rtype: xkcd
        """
        return cls(random.randint(1, cls.latest()))

    def delete(self):
        """
        Deletes the data associated with this xkcd object so that it is reloaded
        the next time it is requested

        :return: None
        """
        del self._raw_json
        del self.json
        self._keep_alive.pop(self._comic, None)
        self._cache.pop(self._comic, None)

    @property
    def explain_xkcd(self):
        """
        :return: The explain xkcd wiki link for this comic
        :rtype: str
        """
        if self._comic is None:
            return constants.explain_xkcd.latest
        return constants.explain_xkcd.for_comic(number=self._comic)

    @property
    def url(self):
        """
        :return: The url for this comic
        :rtype: str
        """
        if self._comic is None:
            return constants.xkcd.latest
        return constants.xkcd.for_comic(number=self._comic)

    @property
    def mobile_url(self):
        """
        :return: The mobile url for this comic
        :rtype: str
        """
        if self._comic is None:
            return constants.xkcd.mobile.latest
        return constants.xkcd.mobile.for_comic(number=self._comic)

    @property
    def num(self):
        return self.json['num']

    def __repr__(self):
        return '{type.__name__}({number})'.format(type=type(self), number=self._comic or '')

    @classmethod
    def load_all(cls, multiprocessed=False):
        """
        Load all the comics into the cache. Note: Takes a lot of time.

        :param bool multiprocessed: Use multiprocessing.Pool instead of
            running in sequence
        :return: None
        """
        xkcd(keep_alive=True).json
        if multiprocessed:
            pool = multiprocessing.Pool(4)
            pool.map(_load_one, cls.range())
            pool.close()
            pool.join()
        else:
            for n in cls.range():
                xkcd(n, keep_alive=True).json

    load_one = staticmethod(_load_one)

    @classmethod
    def delete_all(cls):
        xkcd().delete()
        for n in cls.range():
            xkcd(n).delete()

    @classmethod
    def delete_one(cls, comic):
        xkcd(comic).delete()

    @staticmethod
    def antigravity():
        """???"""
        antigravity = ____(___)
        if antigravity is not _____:
            return ______(antigravity)
        import antigravity
        return antigravity

    def __iter__(self):
        if self._comic is None:
            yield self
            return
        cls = type(self)
        for c in range(self._comic, cls.latest() + 1):
            yield cls(c)

    def next(self):
        """
        Return the next comic. If is the latest comic, raise StopIteration

        :return: Next comic
        :rtype: xkcd
        """
        return self.__next__()

    def back(self):
        """
        Return the previous comic. If is xkcd(1), raise StopIteration.

        :return: Previous comic
        :rtype: xkcd
        """
        if self._comic is None:
            return type(self)(self.latest() - 1)
        if self._comic == 1:
            raise StopIteration
        return type(self)(self._comic - 1)

    def __next__(self):
        if self._comic is None or self._comic == self.latest():
            raise StopIteration
        return type(self)(self._comic + 1)

    def __reversed__(self):
        if self._comic is None:
            comic = self.latest()
        else:
            comic = self._comic
        cls = type(self)
        for i in range(comic - 1, 0, -1):
            yield cls(i)

    @classmethod
    def range(cls, from_=1, to=None, step=1):
        """
        Returns an iterator over specified comics.

        Use negative numbers to specify from the end.

        :param int from_: The comic to start from. Defaults to the first.
        :param Optional[int] to_: The comic to end by (exclusive). Defaults to last + 1.
        :param int step: The step amount. Defaults to one.
        :return: A range over the requested comics.
        """
        if to is None:
            if step < 0:
                to = 0
            else:
                to = cls.latest() + 1

        return range(from_, to, step)

    def __eq__(self, other):
        if isinstance(other, xkcd) and isinstance(self, xkcd):
            if self is other or other.comic == self._comic:
                return True
            if self._comic is None:
                return self.num == other.comic
            if other.comic is None:
                return other.num == self._comic
            return False
        return NotImplemented

    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

    def __lt__(self, other):
        if isinstance(other, xkcd) and isinstance(self, xkcd):
            if self is other or self._comic == other.comic:
                return False
            if self._comic is None:
                return False
            if other.comic is None:
                return True
            return self._comic < other.comic
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, xkcd) and isinstance(self, xkcd):
            if self is other or self._comic == other.comic:
                return True
            if self._comic is None:
                if other.comic is None:
                    return True
                return self.num == other.comic
            if other.comic is None:
                return True
            return self._comic <= other.comic
        return NotImplemented

    def __ge__(self, other):
        lt = self.__lt__(other)
        if lt is NotImplemented:
            return NotImplemented
        return not lt

    def __gt__(self, other):
        le = self.__le__(other)
        if le is NotImplemented:
            return NotImplemented
        return not le
