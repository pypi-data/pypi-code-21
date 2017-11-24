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

import re
import datetime

try:
    import ujson as json
except ImportError:
    import json


class DownloadLinkGenerator:

    BASE = 'https://connect.monstercat.com'
    API_BASE = BASE + '/api'
    RELEASE = API_BASE + '/release'
    PLAYLIST = API_BASE + '/playlist'
    FORMATS = ['mp3_320', 'mp3_128', 'mp3_v0', 'mp3_v2', 'wav', 'flac']

    def release(self, release_id, audio_format):
        if audio_format in self.FORMATS:
            return f'{self.RELEASE}/{release_id}/download?method=download&type={audio_format}'
        else:
            raise ValueError('The audio format inserted is invalid')

    def track(self, release_id, track_id, audio_format):
        if audio_format in self.FORMATS:
            return f'{self.RELEASE}/{release_id}/download?method=download&type={audio_format}&track={track_id}'
        else:
            raise ValueError('The audio format inserted is invalid')

    def playlist(self, playlist_id, audio_format, page=1):
        if audio_format in self.FORMATS:
            return f'{self.PLAYLIST}/{playlist_id}/download?method=download&type={audio_format}&page={page}'
        else:
            raise ValueError('The audio format inserted is invalid')


def to_json(obj):
    if json.__name__ == 'ujson':
        return json.dumps(obj, ensure_ascii=True)
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)


def parse_time(timestamp):
    if timestamp:
        return datetime.datetime(*map(int, re.split(r'[^\d]', timestamp.replace('Z', ''))))
    return None


def find(predicate, items):
    for item in items:
        if predicate(item):
            return item
    return None
