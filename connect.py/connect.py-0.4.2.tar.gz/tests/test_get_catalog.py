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

import unittest
import connect


class TestGetCatalog(unittest.TestCase):
    def setUp(self):
        self.connect = connect.Client()

    def test_release(self):
        release = self.connect.get_release('MC011')
        print(f'\n[connect.Client.get_release]\n{release.title} by {release.artists} had been release on {release.release_date} and has the following track(s):')
        print('\n'.join([f'{track.title} by {track.artists}' for track in release.tracks]))

    def test_playlist(self):
        playlist = self.connect.get_playlist('577ec5395891d31a15b80c39')
        print(f'\n[connect.Client.get_playlist]\nThe playlist with the name {playlist} has the following tracks:')
        for track in playlist.tracks:
            print(f'[{track.release.catalog_id}] {track.title} by {track.artists} from {track.release.title}')

    def test_track(self):
        track = self.connect.get_track('512bdb6db9a8860a11000029')
        print(f'\n[connect.Client.get_track]\n{track.title} by {track.artists} has been featured on the following releases:')
        self.assertEqual(track.artists, str(self.connect.get_artist(track.get_artists()[0].id)))
        release = self.connect.get_release('MC011')
        self.assertEqual([album.id for album in track.albums if album.id == release.id][0], release.id)
        for album in track.albums:
            print('[{0.catalog_id}] {0.title}'.format(self.connect.get_release(album.id)))

    def test_artist(self):
        artist = self.connect.get_artist('gq')
        print(f'\n[connect.Client.get_artist]\n{artist}, is featured on the year(s) {", ".join(str(year) for year in artist.years)} and has released the following:')
        for release in artist.releases:
            if not release.artists.lower() == 'various artists':
                print(f'[{release.catalog_id}] {release.title} with {len(release.tracks)} track(s)')
        print("And appears on:")
        for release in artist.releases:
            if release.artists.lower() == 'various artists':
                print(f'[{release.catalog_id}] {release.title}')

    def tearDown(self):
        self.connect.close()
