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


class Artist:
    """Represents a release from connect.

    Attributes
    ----------
    id: str
        The artist ID.
    name: str
        The artist name.
    vanity_uri: str
        The artist vanity uri.
    profile_image_id: str
        The profile image hash the artist has. Could be None. Soon to be obsolete.
    profile_image_url: str
        Returns the profile image URL that the artist has.
    urls: List[str]
        The artist social media urls.
    years: List[int]
        The artist release years.
    """

    __slots__ = (
        'id', 'name', 'vanity_uri', 'profile_image_id', 'profile_image_url',
        'about', 'bookings', 'management_detail', 'urls', 'years', '_releases', '_http'
    )

    def __init__(self, **kwargs):
        self.id = kwargs.pop('_id')
        self.name = kwargs.pop('name')
        self.vanity_uri = kwargs.pop('vanityUri', None)
        self.profile_image_id = kwargs.pop('profileImageBlobId', None)
        self.profile_image_url = kwargs.pop('profileImageUrl')
        self.about = kwargs.pop('about', None)
        self.bookings = kwargs.pop('bookings', None)
        self.management_detail = kwargs.pop('managementDetail', None)
        self.urls = kwargs.pop('urls')
        self.years = kwargs.pop('years')
        self._http = kwargs.pop('http', None)
        self._releases = {}

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __str__(self):
        return self.name

    def _add_release(self, release):
        self._releases[release.id] = release

    @property
    def releases(self):
        """A list of the artist's releases or appearances."""
        if self._releases:
            return list(self._releases.values())
        else:
            from .http import HTTPClient
            from .release import Release
            http = self._http or HTTPClient()
            releases = http.get_artist_releases(self.id)
            if not self._http:
                http.close()
            for data in releases['results']:
                release = Release(http=self._http, **data)
                self._add_release(release)
            return list(self._releases.values())


class ArtistEntry:
    """Represents an artist entry from a track.

    Attributes
    ----------
    id: str
        The artist ID.
    name: str
        The artist name.
    """

    __slots__ = ('id', 'name')

    def __init__(self, **kwargs):
        self.id = kwargs.pop('artistId')
        self.name = kwargs.pop('name')

    def __eq__(self, other):
        return self.id == other.id and isinstance(other, self.__class__)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return True

    def __str__(self):
        return self.name
