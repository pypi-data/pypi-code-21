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

import sys
import unittest

import async_connect as connect


class TestSearch(unittest.TestCase):
    def setUp(self):
        if sys.version_info[1] == 6:
            import asyncio
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            self.loop = asyncio.get_event_loop()
            self.connect = connect.Client(loop=self.loop)
        else:
            self.connect = connect.Client()
            self.loop = self.connect.loop

    def test_release(self):
        async def test():
            releases = await self.connect.search_release('friends')
            print('\n[connect.Client.search_release] Found the following:')
            for release in releases:
                print('[{0.catalog_id}] Released on {0.release_date}, has {1} track(s) and with the title {0.title}'.format(release, len(await release.tracks.values())))
            self.assertEqual(releases[0], await self.connect.get_release('MCEP071'))

        self.loop.run_until_complete(test())

    def test_release_adv(self):
        async def test():
            releases = await self.connect.search_release_advanced('FTW', 'Lets Be Friends')
            print('\n[connect.Client.search_release_advanced] Found the following:')
            for release in releases:
                print('[{0.catalog_id}] Released on {0.release_date}, has {1} track(s) and with the title {0.title}'.format(release, len(await release.tracks.values())))
            self.assertEqual(releases[0], await self.connect.get_release('MCS194'))

        self.loop.run_until_complete(test())

    def test_track(self):
        async def test():
            tracks = await self.connect.search_track('you')
            print('\n[connect.Client.search_track] Found the following:')
            for track in tracks:
                print(f'{track.title} by {track.artists} with the genre(s) {", ".join(track.genres)} and featured on {len(track.albums)}')
            self.assertEqual(tracks[0], await self.connect.get_track('5175cd4e0695c7ac5d000033'))

        self.loop.run_until_complete(test())

    def test_track_adv(self):
        async def test():
            tracks = await self.connect.search_track_advanced("Do You Don't You", 'Haywyre')
            print('\n[connect.Client.search_track_advanced] Found the following:')
            for track in tracks:
                print(f'{track.title} by {track.artists} with the genre(s) {", ".join(track.genres)} and featured on {len(track.albums)}')
            self.assertEqual(tracks[0], await self.connect.get_track('56a2773c5050dd875854cf85'))

        self.loop.run_until_complete(test())

    def test_artist(self):
        async def test():
            artists = await self.connect.search_artist('grant')
            print('\n[connect.Client.search_artist] Found the following:')
            for artist in artists:
                print("{0.name}, that has {1} release(s) and it's featured on the following year(s): {2}".format(artist, len(await artist.releases.values()),
                                                                                                                 ', '.join(str(year) for year in artist.years)))
            self.assertEqual(artists[1], await self.connect.get_artist('grant'))

        self.loop.run_until_complete(test())

    def tearDown(self):
        self.loop.run_until_complete(self.connect.close())
