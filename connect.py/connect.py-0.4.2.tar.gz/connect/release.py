# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2016-2017 GiovanniMCMXCIX

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from . import utils


class Release:
    """Represents a release from connect.
    
    Attributes
    ----------
    id: str
        The release ID.
    catalog_id: str
        The Catalog ID of the release. Could be None.
    artists: str
        The release artists.
    title: str
        The release title.
    release_date: datetime.datetime
        A naive UTC datetime object containing the time the release was launched.
    type: str
        Release type.
    urls: List[str]
        A list of urls for supporting or listening to the release.
    is_downloadable: bool
        Indicates if the release can be downloaded.
    is_streamable: bool
        Indicates if the release can be streamed.
    in_early_access: bool
        Indicates if the release is in early access for gold users.
    is_free: bool
        Indicates if the track can be downloaded for free.
    """

    __slots__ = (
        'id', 'catalog_id', 'artists', 'title', 'release_date', 'type', 'cover_url', 'urls',
        'is_downloadable', 'is_streamable', 'in_early_access', 'is_free', '_tracks', '_http'
    )

    def __init__(self, **kwargs):
        self.id = kwargs.pop('_id')
        self.catalog_id = kwargs.pop('catalogId', None)
        self.artists = kwargs.pop('renderedArtists', None)
        self.title = kwargs.pop('title', None)
        self.release_date = utils.parse_time(kwargs.pop('releaseDate'))
        self.type = kwargs.pop('type')
        self.cover_url = kwargs.pop('coverUrl')
        self.urls = kwargs.pop('urls')
        self.is_downloadable = kwargs.pop('downloadable', None)
        self.is_streamable = kwargs.pop('streamable', None)
        self.in_early_access = kwargs.pop('inEarlyAccess', None)
        self.is_free = kwargs.pop('freeDownloadForUsers', None)
        self._http = kwargs.pop('http', None)
        self._tracks = {}

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __str__(self):
        return f'{self.artists} - {self.title}'

    def thumbnails(self, resolution: int) -> str:
        """Returns a hash to a bound resolution."""
        return f'{self.cover_url}?image_width={resolution}'

    def _add_track(self, track):
        self._tracks[track.id] = track

    @property
    def tracks(self):
        """Returns a list of connect.Tracks items."""
        if self._tracks:
            return list(self._tracks.values())
        else:
            from .http import HTTPClient
            from .track import Track
            http = self._http or HTTPClient()
            tracklist = http.get_release_tracklist(self.id)
            if not self._http:
                http.close()
            for data in tracklist['results']:
                track = Track(**data)
                self._add_track(track)
            return list(self._tracks.values())


class ReleaseEntry:
    """Represents a release from a playlist track.

    Attributes
    ----------
    id: str
        The release ID.
    catalog_id: str
        The Catalog ID of the release. Could be None.
    title: str
        The release title.
    release_date: datetime.datetime
        A naive UTC datetime object containing the time the release was launched.
    is_downloadable: bool
        Indicates if the release can be downloaded.
    is_streamable: bool
        Indicates if the release can be streamed.
    in_early_access: bool
        Indicates if the release is in early access for gold users.
    """

    __slots__ = ('id', 'catalog_id', 'title', 'release_date', 'is_downloadable', 'is_streamable', 'in_early_access')

    def __init__(self, **kwargs):
        self.id = kwargs.pop('_id')
        self.catalog_id = kwargs.pop('catalogId', None)
        self.title = kwargs.pop('title')
        self.release_date = utils.parse_time(kwargs.pop('releaseDate'))
        self.is_downloadable = kwargs.pop('downloadable', None)
        self.is_streamable = kwargs.pop('streamable', None)
        self.in_early_access = kwargs.pop('inEarlyAccess', None)

    def __eq__(self, other):
        return self.id == other.id and isinstance(other, self.__class__)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return True

    def __str__(self):
        return self.title


class Album:
    """Represents a release from a track.

    Attributes
    ----------
    id: str
        The release ID.
    track_number: int
        Placement in a release.
    stream_id: str
        The stream hash of the release.
    """

    __slots__ = ('id', 'track_number', 'stream_id')

    def __init__(self, **kwargs):
        self.id = kwargs.pop('albumId')
        self.track_number = kwargs.pop('trackNumber')
        stream_id = kwargs.pop('streamHash')
        self.stream_id = None if stream_id in [None, ''] else stream_id

    def __eq__(self, other):
        return self.id == other.id and isinstance(other, self.__class__)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return True

    @property
    def stream_url(self):
        """Returns a friendly URL version of the stream_id variable the release has."""
        if not self.stream_id:
            return None
        else:
            return f'https://s3.amazonaws.com/data.monstercat.com/blobs/{self.stream_id}'
