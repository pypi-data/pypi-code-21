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

import requests
import sys
import re

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

    def __init__(self):
        self.session = requests.Session()
        self.download_link_gen = utils.DownloadLinkGenerator()

        user_agent = 'ConnectBot (https://github.com/GiovanniMCMXCIX/connect.py {0}) ' \
                     'Python/{1[0]}.{1[1]} requests/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, requests.__version__)

    def request(self, method, url, **kwargs):
        headers = {
            'User-Agent': self.user_agent
        }

        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = utils.to_json(kwargs.pop('json'))

        kwargs['headers'] = headers
        response = self.session.request(method, url, **kwargs)
        try:
            data = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            data = {'message': response.text} if response.text else None
        except ValueError:
            data = {'message': response.text} if response.text else None

        if 300 > response.status_code >= 200:
            return data
        elif response.status_code == 401:
            raise Unauthorized(data.pop('message', 'Unknown error'))
        elif response.status_code == 403:
            raise Forbidden(data.pop('message', 'Unknown error'))
        elif response.status_code == 404:
            raise NotFound(data.pop('message', 'Unknown error'))
        else:
            raise HTTPSException(data.pop('message', 'Unknown error'), response)

    def download(self, url, path, chunk_size=4096, **kwargs):
        def raise_error(error, resp, use_resp=False):
            text = resp.text
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
        kwargs['headers'] = {'User-Agent': self.user_agent}
        kwargs['stream'] = True
        filename = kwargs.pop('filename', None)
        response = self.request('GET', url, **kwargs)
        if 300 > response.status_code >= 200:
            if not filename:
                filename = str.replace(re.findall("filename=(.+)", response.headers['content-disposition'])[0], "\"", "")
            with open(f'{path}/{filename}', 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
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

    def close(self):
        self.session.close()

    def email_sign_in(self, email, password):
        payload = {
            'email': email,
            'password': password
        }
        self.request('POST', self.SIGN_IN, json=payload)

    def two_feature_sign_in(self, email, password, token):
        payload = {
            'token': token
        }
        self.email_sign_in(email, password)
        self.request('POST', f'{self.SIGN_IN}/token', json=payload)

    def is_signed_in(self):
        response = self.request('GET', f'{self.SELF}/session')
        if not response.get('user'):
            return False
        if response.get('user').get('subscriber', False) is True:
            return True

    def sign_out(self):
        self.request('POST', self.SIGN_OUT)

    def create_playlist(self, name, *, public=False, entries=None):
        payload = {
            'name': name,
            'public': public
        }
        if entries:
            payload['tracks'] = entries
        return self.request('POST', f'{self.PLAYLIST}', json=payload)

    def edit_profile(self, *, name=None, real_name=None, location=None, password=None):
        payload = {}
        if name:
            payload['name'] = name
        if real_name:
            payload['realName'] = real_name
        if location:
            payload['location'] = location
        if password:
            payload['password'] = password
        return self.request('PATCH', self.SELF, json=payload)

    def edit_playlist(self, playlist_id, *, name=None, public=False):
        payload = {}
        if name:
            payload['name'] = name
        if public:
            payload['public'] = public
        return self.request('PATCH', f'{self.PLAYLIST}/{playlist_id}', json=payload)

    def add_playlist_track(self, playlist_id, track_id, release_id):
        playlist = self.get_playlist(playlist_id)
        playlist['tracks'].append({'trackId': track_id, 'releaseId': release_id})
        return self.request('PUT', f'{self.PLAYLIST}/{playlist_id}', json=playlist)

    def add_playlist_tracks(self, playlist_id, entries):
        playlist = self.get_playlist(playlist_id)
        for entry in entries:
            playlist['tracks'].append(entry)
        return self.request('PUT', f'{self.PLAYLIST}/{playlist_id}', json=playlist)

    def add_reddit_username(self, username):
        payload = {
            'redditUsername': username
        }
        self.request('POST', f'{self.SELF}/update-reddit', json=payload)

    def delete_playlist(self, playlist_id):
        self.request('DELETE', f'{self.PLAYLIST}/{playlist_id}')

    def delete_playlist_track(self, playlist_id, track_id):
        playlist = self.get_playlist(playlist_id)
        track = [item for item in playlist['tracks'] if item['trackId'] == track_id][0]
        del playlist['tracks'][playlist['tracks'].index(track)]
        return self.request('PUT', f'{self.PLAYLIST}/{playlist_id}', json=playlist)

    def download_release(self, album_id, path, audio_format, chunk_size=8192):
        return self.download(self.download_link_gen.release(album_id, audio_format), path, chunk_size=chunk_size)

    def download_track(self, album_id, track_id, path, audio_format, chunk_size=8192):
        return self.download(self.download_link_gen.track(album_id, track_id, audio_format), path, chunk_size=chunk_size)

    def download_playlist(self, playlist_id, page, path, audio_format, chunk_size=8192):
        return self.download(self.download_link_gen.playlist(playlist_id, audio_format, page), path, chunk_size=chunk_size)

    def get_self(self):
        return self.request('GET', self.SELF)

    def get_discord_invite(self):
        return self.request('GET', f'{self.SELF}/discord/gold')

    def get_release(self, catalog_id):
        return self.request('GET', f'{self.RELEASE}/{catalog_id}')

    def get_release_tracklist(self, release_id):
        return self.request('GET', f'{self.RELEASE}/{release_id}/tracks')

    def get_track(self, track_id):
        return self.request('GET', f'{self.TRACK}/{track_id}')

    def get_artist(self, artist_id):
        return self.request('GET', f'{self.ARTIST}/{artist_id}')

    def get_artist_releases(self, artist_id):
        return self.request('GET', f'{self.ARTIST}/{artist_id}/releases')

    def get_playlist(self, playlist_id):
        return self.request('GET', f'{self.PLAYLIST}/{playlist_id}')

    def get_playlist_tracklist(self, playlist_id):
        return self.request('GET', f'{self.PLAYLIST}/{playlist_id}/tracks')

    def get_browse_entries(self, *, types=None, genres=None, tags=None, limit=None, skip=None):
        query = []
        if types:
            query.append(f'&types={",".join(types)}')
        if genres:
            query.append(f'&genres={",".join(genres)}')
        if tags:
            query.append(f'&tags={",".join(tags)}')
        return self.request('GET', f'{self.BROWSE}?limit={limit}&skip={skip}{"".join(query)}')

    def get_all_releases(self, *, singles=True, eps=True, albums=True, podcasts=False, limit=None, skip=None):
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
            return self.request('GET', f'{self.RELEASE}?fuzzyOr=type,None')
        else:
            return self.request('GET', f'{self.RELEASE}?fuzzyOr={",".join(query)}&limit={limit}&skip={skip}')

    def get_all_tracks(self, limit=None, skip=None):
        return self.request('GET', f'{self.TRACK}?limit={limit}&skip{skip}')

    def get_all_artists(self, year=None, limit=None, skip=None):
        base = f'{self.ARTIST}?limit={limit}&skip={skip}'
        if year:
            base = f'{base}&fuzzy=year,{year}'
        return self.request('GET', base)

    def get_all_playlists(self, *, limit=None, skip=None):
        return self.request('GET', f'{self.PLAYLIST}?limit={limit}&skip={skip}')
