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

from .release import ReleaseEntry
from .track import Track


class Playlist:
    """Represents a release from connect.

        Attributes
        ----------
        id: str
            The playlist ID.
        name: str
            The playlist name.
        owner_id: str
            The owner id.
        is_public: bool
            If the playlist is public.
        is_deleted: bool
            If the playlist is deleted.
        """

    __slots__ = ('id', 'name', 'owner_id', 'is_public', 'is_deleted', '_tracks', '_http')

    def __init__(self, **kwargs):
        self.id = kwargs.pop('_id')
        self.name = kwargs.pop('name')
        self.owner_id = kwargs.pop('userId')
        self.is_public = kwargs.pop('public')
        self.is_deleted = kwargs.pop('deleted')
        self._http = kwargs.pop('http', None)
        self._tracks = {}

    def __eq__(self, other):
        return self.id == other.id and isinstance(other, self.__class__)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return True

    def __str__(self):
        return self.name

    @property
    def tracks(self):
        """Returns a list of connect.playlist.PlaylistEntry items."""
        if self._tracks:
            return list(self._tracks.values())
        else:
            from .http import HTTPClient
            http = self._http or HTTPClient()
            tracklist = http.get_playlist_tracklist(self.id)
            if not self._http:
                http.close()
            for data in tracklist['results']:
                track = PlaylistEntry(**data)
                self._add_track(track)
            return list(self._tracks.values())

    def _add_track(self, track):
        self._tracks[track.id] = track


class PlaylistEntry(Track):
    """Represents a track from a playlist.

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
        It usually returns a list with one item that is the same with :attr:`connect.Track.genre`
    release: connect.release.ReleaseEntry
        Release that the playlist entry is a part of.
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

    __slots__ = 'release'

    def __init__(self, **kwargs):
        self.release = ReleaseEntry(**kwargs.pop('release'))
        super().__init__(**kwargs)
