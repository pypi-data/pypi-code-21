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
import re
import sys

import aiohttp

try:
    import ujson as json
except ImportError:
    import json

from .errors import HTTPSException, Unauthorized, Forbidden, NotFound
from . import utils, __version__


class HTTPClient:
    BASE = 'https://connect.monstercat.com'
    SIGN_IN = BASE + '/signin'
    SIGN_OUT = BASE + '/signout'
    API_BASE = BASE + '/api'
    SELF = API_BASE + '/self'
    CATALOG = API_BASE + '/catalog'
    PLAYLIST = API_BASE + '/playlist'
    TRACK = CATALOG + '/track'
    RELEASE = CATALOG + '/release'
    ARTIST = CATALOG + '/artist'
    BROWSE = CATALOG + '/browse'
    BROWSE_FILTERS = BROWSE + '/filters'

    def __init__(self, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.download_link_gen = utils.DownloadLinkGenerator()
        user_agent = 'AsyncConnectBot (https://github.com/GiovanniMCMXCIX/async-connect.py {0}) ' \
                     'Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    async def request(self, method, url, **kwargs):
        headers = {
            'User-Agent': self.user_agent
        }

        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = utils.to_json(kwargs.pop('json'))

        kwargs['headers'] = headers
        async with self.session.request(method, url, **kwargs) as response:
            text = await response.text()
            try:
                data = json.loads(text)
            except json.decoder.JSONDecodeError:
                data = {'message': text} if text else None
            except ValueError:
                data = {'message': text} if text else None

            if 300 > response.status >= 200:
                return data
            elif response.status == 401:
                raise Unauthorized(data.pop('message', 'Unknown error'))
            elif response.status == 403:
                raise Forbidden(data.pop('message', 'Unknown error'))
            elif response.status == 404:
                raise NotFound(data.pop('message', 'Unknown error'))
            else:
                raise HTTPSException(data.pop('message', 'Unknown error'), response)

    async def download(self, url, path, chunk_size=4096, **kwargs):
        filename = kwargs.pop('filename', None)
        kwargs['headers'] = {'User-Agent': self.user_agent}
        async with self.session.request('GET', url, **kwargs) as response:
            async def raise_error(error, resp, use_resp=False):
                text = await resp.text()
                try:
                    if use_resp:
                        raise error(json.loads(text).pop('message', 'Unknown error'), response)
                    else:
                        raise error(json.loads(text).pop('message', 'Unknown error'))
                except json.decoder.JSONDecodeError:
                    if use_resp:
                        raise error({'message': text} if text else 'Unknown error', response)
                    else:
                        raise error({'message': text} if text else 'Unknown error')
                except ValueError:
                    if use_resp:
                        raise error({'message': text} if text else 'Unknown error', response)
                    else:
                        raise error({'message': text} if text else 'Unknown error')

            if 300 > response.status >= 200:
                if not filename:
                    filename = str.replace(re.findall("filename=(.+)", response.headers['content-disposition'])[0], "\"", "")
                with open(f'{path}/{filename}', 'wb') as file:
                    while True:
                        chunk = await response.content.read(chunk_size)
                        if not chunk:
                            break
                        file.write(chunk)
                return True
            elif response.status == 401:
                raise_error(Unauthorized, response)
            elif response.status == 403:
                raise_error(Forbidden, response)
            elif response.status == 404:
                raise_error(NotFound, response)
            else:
                raise_error(HTTPSException, response, True)

    async def close(self):
        await self.session.close()

    async def email_sign_in(self, email, password):
        payload = {
            'email': email,
            'password': password
        }
        await self.request('POST', self.SIGN_IN, json=payload)

    async def two_feature_sign_in(self, email, password, token):
        payload = {
            'token': token
        }
        await self.email_sign_in(email, password)
        await self.request('POST', f'{self.SIGN_IN}/token', json=payload)

    async def is_signed_in(self):
        response = await self.request('GET', f'{self.SELF}/session')
        if not response.get('user'):
            return False
        if response.get('user').get('subscriber', False) is True:
            return True

    async def sign_out(self):
        await self.request('POST', self.SIGN_OUT)

    async def create_playlist(self, name, *, public=False, entries=None):
        payload = {
            'name': name,
            'public': public
        }
        if entries:
            payload['tracks'] = entries
        return await self.request('POST', f'{self.PLAYLIST}', json=payload)

    async def edit_profile(self, *, name=None, real_name=None, location=None, password=None):
        payload = {}
        if name:
            payload['name'] = name
        if real_name:
            payload['realName'] = real_name
        if location:
            payload['location'] = location
        if password:
            payload['password'] = password
        return await self.request('PATCH', self.SELF, json=payload)

    async def edit_playlist(self, playlist_id, *, name=None, public=False):
        payload = {}
        if name:
            payload['name'] = name
        if public:
            payload['public'] = public
        return await self.request('PATCH', f'{self.PLAYLIST}/{playlist_id}', json=payload)

    async def add_playlist_track(self, playlist_id, track_id, release_id):
        playlist = await self.get_playlist(playlist_id)
        playlist['tracks'].append({'trackId': track_id, 'releaseId': release_id})
        return await self.request('PUT', f'{self.PLAYLIST}/{playlist_id}', json=playlist)

    async def add_playlist_tracks(self, playlist_id, entries):
        playlist = await self.get_playlist(playlist_id)
        for entry in entries:
            playlist['tracks'].append(entry)
        return await self.request('PUT', f'{self.PLAYLIST}/{playlist_id}', json=playlist)

    async def add_reddit_username(self, username):
        payload = {
            'redditUsername': username
        }
        await self.request('POST', f'{self.SELF}/update-reddit', json=payload)

    async def delete_playlist(self, playlist_id):
        await self.request('DELETE', f'{self.PLAYLIST}/{playlist_id}')

    async def delete_playlist_track(self, playlist_id, track_id):
        playlist = await self.get_playlist(playlist_id)
        track = [item for item in playlist['tracks'] if item['trackId'] == track_id][0]
        del playlist['tracks'][playlist['tracks'].index(track)]
        return await self.request('PUT', f'{self.PLAYLIST}/{playlist_id}', json=playlist)

    async def download_release(self, album_id, path, audio_format, chunk_size=8192):
        return await self.download(self.download_link_gen.release(album_id, audio_format), path, chunk_size=chunk_size)

    async def download_track(self, album_id, track_id, path, audio_format, chunk_size=8192):
        return await self.download(self.download_link_gen.track(album_id, track_id, audio_format), path, chunk_size=chunk_size)

    async def download_playlist(self, playlist_id, page, path, audio_format, chunk_size=8192):
        return await self.download(self.download_link_gen.playlist(playlist_id, audio_format, page), path, chunk_size=chunk_size)

    async def get_self(self):
        return await self.request('GET', self.SELF)

    async def get_discord_invite(self):
        return await self.request('GET', f'{self.SELF}/discord/gold')

    async def get_release(self, catalog_id):
        return await self.request('GET', f'{self.RELEASE}/{catalog_id}')

    async def get_release_tracklist(self, release_id):
        return await self.request('GET', f'{self.RELEASE}/{release_id}/tracks')

    async def get_track(self, track_id):
        return await self.request('GET', f'{self.TRACK}/{track_id}')

    async def get_artist(self, artist_id):
        return await self.request('GET', f'{self.ARTIST}/{artist_id}')

    async def get_artist_releases(self, artist_id):
        return await self.request('GET', f'{self.ARTIST}/{artist_id}/releases')

    async def get_playlist(self, playlist_id):
        return await self.request('GET', f'{self.PLAYLIST}/{playlist_id}')

    async def get_playlist_tracklist(self, playlist_id):
        return await self.request('GET', f'{self.PLAYLIST}/{playlist_id}/tracks')

    async def get_browse_entries(self, *, types=None, genres=None, tags=None, limit=None, skip=None):
        query = []
        if types:
            query.append(f'&types={",".join(types)}')
        if genres:
            query.append(f'&genres={",".join(genres)}')
        if tags:
            query.append(f'&tags={",".join(tags)}')
        return await self.request('GET', f'{self.BROWSE}?limit={limit}&skip={skip}{"".join(query)}')

    async def get_all_releases(self, *, singles=True, eps=True, albums=True, podcasts=False, limit=None, skip=None):
        query = []
        if singles:
            query.append('type,Single')
        if eps:
            query.append('type,EP')
        if albums:
            query.append('type,Album')
        if podcasts:
            query.append('type,Podcast')
        if not singles and not eps and not albums and not podcasts:
            return await self.request('GET', f'{self.RELEASE}?fuzzyOr=type,None')
        else:
            return await self.request('GET', f'{self.RELEASE}?fuzzyOr={",".join(query)}&limit={limit}&skip={skip}')

    async def get_all_tracks(self, limit=None, skip=None):
        return await self.request('GET', f'{self.TRACK}?limit={limit}&skip{skip}')

    async def get_all_artists(self, year=None, limit=None, skip=None):
        base = f'{self.ARTIST}?limit={limit}&skip={skip}'
        if year:
            base = f'{base}&fuzzy=year,{year}'
        return await self.request('GET', base)

    async def get_all_playlists(self, *, limit=None, skip=None):
        return await self.request('GET', f'{self.PLAYLIST}?limit={limit}&skip={skip}')
