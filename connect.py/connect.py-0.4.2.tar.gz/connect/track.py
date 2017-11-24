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

from .release import Release, Album
from .artist import ArtistEntry
from typing import List


class Track:
    """Represents a track from connect.

    Attributes
    ----------
    id: str
        The track ID.
    artists: str
        The track artists.
    title: str
        The track title.
    duration: int
        The track duration.
    bpm: int
        The track BPM.
    genre: str
        The track genre.
    genres: List[str]
        It usually returns a list with one item that is the same with :attr:`connect.Track.genre`.
    tags: List[str]
        The track tags.
    is_downloadable: bool
        Indicates if the track can be downloaded.
    is_streamable: bool
        Indicates if the track can be streamed.
    in_early_access: bool
        Indicates if the track is in early access for gold users.
    is_free: bool
        Indicates if the track can be downloaded for free.
    """

    __slots__ = (
        'id', 'artists', 'title', 'duration', 'bpm', 'genre', 'genres', 'tags', 'is_downloadable', 'is_streamable', 'in_early_access',
        'is_free', '_albums_raw', '_artists_raw', '_featuring_raw', '_remixers_raw', '_albums', '_artists', '_featuring', '_remixers'
    )

    def __init__(self, **kwargs):
        self.id = kwargs.pop('_id')
        self.artists = kwargs.pop('artistsTitle', None)
        self.title = kwargs.pop('title', None)
        duration = kwargs.pop('duration', None)
        bpm = kwargs.pop('bpm', None)
        self.duration = None if not duration else round(duration)
        self.bpm = None if not bpm else round(bpm)
        self.genre = kwargs.pop('genre', None)
        self.genres = kwargs.pop('genres')
        self.tags = kwargs.pop('tags')
        self.is_downloadable = kwargs.pop('downloadable', None)
        self.is_streamable = kwargs.pop('streamable', None)
        self.in_early_access = kwargs.pop('inEarlyAccess', None)
        self.is_free = kwargs.pop('freeDownloadForUsers', None)
        self._albums_raw = kwargs.pop('albums')
        self._artists_raw = kwargs.pop('artists')
        self._featuring_raw = kwargs.pop('featuring')
        self._remixers_raw = kwargs.pop('remixers')
        self._albums = {}
        self._artists = {}
        self._featuring = {}
        self._remixers = {}
        self._from_data()

    def __eq__(self, other):
        return self.id == other.id and isinstance(other, self.__class__)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return True

    def __str__(self):
        return f'{self.artists} - {self.title}'

    @property
    def albums(self):
        """A list of Albums that this track is a part of."""
        return list(self._albums.values())

    def get_artists(self) -> List[ArtistEntry]:
        """A list of artists that composed the track."""
        return list(self._artists.values())

    def get_featuring_artists(self) -> List[ArtistEntry]:
        """A list of artists that are featured on this track."""
        return list(self._featuring.values())

    def get_remixers(self) -> List[ArtistEntry]:
        """A list of artists that remixed this track"""
        return list(self._remixers.values())

    @staticmethod
    def _add_to_dict(class_used, dict_to_add):
        dict_to_add[class_used.id] = class_used

    def _from_data(self):
        for data in self._albums_raw:
            album = Album(**data)
            self._add_to_dict(album, self._albums)

        for data in self._artists_raw:
            artist = ArtistEntry(**data)
            self._add_to_dict(artist, self._artists)

        for data in self._featuring_raw:
            artist = ArtistEntry(**data)
            self._add_to_dict(artist, self._featuring)

        for data in self._remixers_raw:
            artist = ArtistEntry(**data)
            self._add_to_dict(artist, self._remixers)


class BrowseEntry(Track):
    """Represents a track from the browse endpoint.

    Attributes
    ----------
    id: str
        The track ID.
    artists: str
        The track artists.
    title: str
        The track title.
    duration: int
        The track duration.
    bpm: int
        The track BPM.
    genre: str
        The track genre.
    genres: List[str]
        It usually returns a list with one item that is the same with :attr:`connect.Track.genre`.
    release: connect.Release
        Release that this entry is a part of.
    albums: connect.release.Album
        Album that this entry is a part of.
    tags: List[str]
        The track tags.
    is_downloadable: bool
        Indicates if the track can be downloaded.
    is_streamable: bool
        Indicates if the track can be streamed.
    in_early_access: bool
        Indicates if the track is in early access for gold users.
    is_free: bool
        Indicates if the track can be downloaded for free.
    """

    __slots__ = ('release', '_albums', '_albums_raw')

    def __init__(self, **kwargs):
        self.release = Release(**kwargs.pop('release'))
        self._albums = self._albums_raw = Album(**kwargs.pop('albums'))
        super().__init__(**kwargs)

    @property
    def albums(self):
        return self._albums

    def _from_data(self):
        for data in self._artists_raw:
            artist = ArtistEntry(**data)
            self._add_to_dict(artist, self._artists)

        for data in self._featuring_raw:
            artist = ArtistEntry(**data)
            self._add_to_dict(artist, self._featuring)

        for data in self._remixers_raw:
            artist = ArtistEntry(**data)
            self._add_to_dict(artist, self._remixers)
