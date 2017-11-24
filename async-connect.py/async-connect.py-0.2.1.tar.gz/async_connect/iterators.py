# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2017 GiovanniMCMXCIX

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

import asyncio
from typing import AsyncIterator

from .http import HTTPClient


class _AsyncIterator(AsyncIterator):
    def __init__(self, *, http=None, loop=None):
        self.loop = loop
        self.items = asyncio.Queue(loop=self.loop)
        self._http = http
        self._request = True

    async def __anext__(self):
        if self.items.empty() and self._request:
            await self.request_data()
            self._request = False
        try:
            value = self.items.get_nowait()
        except asyncio.QueueEmpty:
            raise StopAsyncIteration()
        else:
            return value

    async def values(self) -> list:
        await self.request_data()
        return list(self.items._queue)

    async def request_data(self):
        pass


class ReleaseIterator(_AsyncIterator):
    def __init__(self, release_id: str, *, http=None, loop=None):
        super().__init__(http=http, loop=loop)
        self.id = release_id

    async def request_data(self):
        from .track import Track
        http = self._http or HTTPClient(loop=self.loop)
        for data in (await http.get_release_tracklist(self.id))['results']:
            track = Track(**data)
            self.items.put_nowait(track)
        if not self._http:
            await http.close()


class PlaylistIterator(_AsyncIterator):
    def __init__(self, playlist_id: str, *, http=None, loop=None):
        super().__init__(http=http, loop=loop)
        self.id = playlist_id

    async def request_data(self):
        from .playlist import PlaylistEntry
        http = self._http or HTTPClient(loop=self.loop)
        for data in (await http.get_playlist_tracklist(self.id))['results']:
            track = PlaylistEntry(**data)
            self.items.put_nowait(track)
        if not self._http:
            await http.close()


class ArtistIterator(_AsyncIterator):
    def __init__(self, artist_id: str, *, http=None, loop=None):
        super().__init__(http=http, loop=loop)
        self.id = artist_id

    async def request_data(self):
        from .release import Release
        http = self._http or HTTPClient(loop=self.loop)
        for data in (await http.get_artist_releases(self.id))['results']:
            release = Release(loop=self.loop, http=self._http, **data)
            self.items.put_nowait(release)
        if not self._http:
            await http.close()
