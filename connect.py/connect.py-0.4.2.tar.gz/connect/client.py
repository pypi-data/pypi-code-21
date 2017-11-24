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

from .http import HTTPClient
from .errors import NotFound
from .release import Release
from .track import Track, BrowseEntry
from .artist import Artist
from .playlist import Playlist
from .utils import find
from typing import List, Tuple
from urllib.parse import quote


class Client:
    def __init__(self):
        self.http = HTTPClient()
        self.browse_filters = self.http.request('GET', self.http.BROWSE_FILTERS)
        self._is_closed = False

    def sign_in(self, email: str, password: str, token: int = None):
        """Logs in the client with the specified credentials.

        Parameters
        ----------
        email: str
            Email that the client should use to sign in.
        password: str
            Password that the client should use to sign in.
        token: int
            Token that the client should use to sign in. (2FA Only)

        Raises
        ------
        HTTPSException
            Invalid email, password or token.
        """
        if not token:
            self.http.email_sign_in(email, password)
        else:
            self.http.two_feature_sign_in(email, password, token)

    @property
    def is_signed_in(self):
        """bool: Indicates if the client has logged in successfully."""
        return self.http.is_signed_in()

    def sign_out(self):
        """Logs out of Monstercat Connect and closes all connections."""
        self.http.sign_out()
        self.close()

    def close(self):
        """Closes all connections."""
        if self._is_closed:
            return
        else:
            self.http.close()
            self._is_closed = True

    def create_playlist(self, name: str, *, public: bool = False, entries: List[Tuple[Track, Release]] = None) -> Playlist:
        """Creates a playlist.

        Parameters
        ----------
        name: str
           Name of the playlist that is going to be created.
        public: bool
           If the playlist that is going to be created should be public or not.
        entries: List[Tuple[connect.Track, connect.Release]]
           The tracks that would be added to the playlist that is created.

        Raises
        ------
        ValueError
           Some of the given entries are not valid.
        Forbidden
           The client isn't signed in.

        Returns
        -------
        Playlist
            The playlist that was created.
        """
        if entries:
            json_entries = []
            for entry in entries:
                if find(lambda a: a.id == entry[1].id, entry[0].albums):
                    json_entries.append({'trackId': entry[0].id, 'releaseId': entry[1].id})
                else:
                    raise ValueError(f'The track "{entry[0]}" is not in the release\'s "{entry[1]}" track list.')
            return Playlist(http=self.http, **self.http.create_playlist(name=name, public=public, entries=json_entries))
        else:
            return Playlist(http=self.http, **self.http.create_playlist(name=name, public=public))

    def edit_playlist(self, playlist: Playlist, *, name: str = None, public: bool = False) -> Playlist:
        """Edits a playlist.

        Parameters
        ----------
        playlist: connect.Playlist
            Playlist that is gonna be edited.
        name: str
            New name of the playlist that is edited
        public: bool
            If the playlist should be public or not after it's edited

        Raises
        ------
        Forbidden
            The client isn't signed in/ You don't own the playlist.

        Returns
        -------
        Playlist
            The playlist that was edited.
        """
        return Playlist(http=self.http, **self.http.edit_playlist(playlist_id=playlist.id, name=name, public=public))

    def edit_profile(self, *, name: str = None, real_name: str = None, location: str = None, password: str = None):
        """Edits the current profile of the client.

        Parameters
        ----------
        name: str
            New name of the account's profile.
        real_name: str
            New real name of the account's profile.
        location: str
            New location of the account's profile. (buggy)
        password: str
            New password of the account.

        Raises
        ------
        Forbidden
            The client isn't signed in.
        """
        self.http.edit_profile(name=name, real_name=real_name, location=location, password=password)

    def add_playlist_track(self, playlist: Playlist, track: Track, release: Release) -> Playlist:
        """Adds a track to a playlist's tracklist

        Parameters
        ----------
        playlist: connect.Playlist
            Playlist that the track are going added to.
        track: connect.Track
            Track that is added to the given playlist.
        release: connect.Release
            Release where the track is originated from.
        Raises
        ------
        ValueError
           Some of the given track, release combination is not valid.
        Forbidden
           The client isn't signed in/ You don't own the given playlist.

        Returns
        -------
        Playlist
            The playlist with the track that was added.
        """
        if find(lambda a: a.id == release.id, track.albums):
            return Playlist(http=self.http, **self.http.add_playlist_track(playlist_id=playlist.id, track_id=track.id, release_id=release.id))
        else:
            raise ValueError(f'The track "{track}" is not in the release\'s "{release}" track list.')

    def add_playlist_tracks(self, playlist: Playlist, entries: List[Tuple[Track, Release]]) -> Playlist:
        """Adds a track to a playlist's tracklist

        Parameters
        ----------
        playlist: connect.Playlist
            Playlist that the tracks are going added to.
        entries: List[Tuple[connect.Track, connect.Release]]
            Tracks that would be added to the given playlist.

        Raises
        ------
        ValueError
           Some of the given track, release combination is not valid.
        Forbidden
           The client isn't signed in/ You don't own the given playlist.

        Returns
        -------
        Playlist
            The playlist with the tracks that were added.
        """
        json_entries = []
        for entry in entries:
            if find(lambda a: a.id == entry[1].id, entry[0].albums):
                json_entries.append({'trackId': entry[0].id, 'releaseId': entry[1].id})
            else:
                raise ValueError(f'The track "{entry[0]}" is not in the release\'s "{entry[1]}" track list.')
        return Playlist(http=self.http, **self.http.add_playlist_tracks(playlist_id=playlist.id, entries=json_entries))

    def add_reddit_username(self, username: str):
        """Adds the reddit username to the current profile of the client.

        Parameters
        ----------
        username: str
            Reddit username that is added to the monstercat account.

        Raises
        ------
        NotFound
            "I need to buy monstercat gold again in order to finish this library" ~ Library Author
        """
        self.http.add_reddit_username(username)

    def delete_playlist(self, playlist: Playlist):
        """Deletes a playlist.

        Parameters
        ----------
        playlist: connect.Playlist
           The playlist that is deleted.

        Raises
        ------
        Forbidden
            The client isn't signed in/ You don't own the given playlist.
        """
        self.http.delete_playlist(playlist.id)

    def delete_playlist_track(self, playlist: Playlist, track: Track) -> Playlist:
        """Deletes a track from a playlist's tracklist.

        Parameters
        ----------
        playlist: connect.Playlist
           Playlist from where the client should remove the given track.
        track: connect.Track
           Track that is deleted from the tracklist of the given playlist.

        Raises
        ------
        Forbidden
            The client isn't signed in/ You don't own the given playlist.

        Returns
        -------
        Playlist
            The playlist with the track that was deleted.
        """
        return Playlist(http=self.http, **self.http.delete_playlist_track(playlist_id=playlist.id, track_id=track.id))

    def get_discord_invite(self) -> str:
        """Gets an invite for the gold discord channel on the monstercat discord guild.
        The client needs gold subscription in order to get the invite for that channel.

        Raises
        ------
        NotFound
            "I need to buy monstercat gold again in order to finish this library" ~ Library Author
        """
        return self.http.get_discord_invite()

    def get_release(self, catalog_id: str) -> Release:
        """Returns a release with the given ID.

        Parameters
        ----------
        catalog_id: str
           The id of the release that the client should get.

        Raises
        ------
        NotFound
            The client couldn't get the release.

        Returns
        -------
        Release
            Release that was requested with the given ID/catalog ID.
        """
        return Release(http=self.http, **self.http.get_release(catalog_id))

    def get_track(self, track_id: str) -> Track:
        """Returns a track with the given ID.

        Parameters
        ----------
        track_id: str
            The id of the track that the client should get.

        Raises
        ------
        NotFound
            The client couldn't get the track.


        Returns
        -------
        Track
            Track that was requested with the given ID.
        """
        return Track(http=self.http, **self.http.get_track(track_id))

    def get_artist(self, artist_id: str) -> Artist:
        """Returns a artist with the given ID.

        Parameters
        ----------
        artist_id: str
           The id/vanity_uri of the artist that the client should get.

        Raises
        ------
        NotFound
            The client couldn't get the artist.

        Returns
        -------
        Artist
            Artist that was requested with the given ID/vanity uri.
        """
        return Artist(http=self.http, **self.http.get_artist(artist_id))

    def get_playlist(self, playlist_id: str) -> Playlist:
        """Returns a playlist with the given ID.

        Parameters
        ----------
        playlist_id: str
            The id of the playlist that the client should get.

        Raises
        ------
        Forbidden
            The client can't access a private playlist.
        NotFound
            The client couldn't get the playlist.

        Returns
        -------
        Playlist
            Playlist that was requested with the given ID.
        """
        return Playlist(http=self.http, **self.http.get_playlist(playlist_id))

    def get_all_releases(self, *, singles: bool = True, eps: bool = True, albums: bool = True, podcasts: bool = False, limit: int = None, skip: int = None) -> List[Release]:
        """Retrieves every release the client can access.

        Parameters
        ----------
        singles: bool
           If the client should get singles.
        eps: bool
           If the client should get EPs.
        albums: bool
           If the client should get albums.
        podcasts: bool
           If the client should get podcasts.
        limit: int
           The limit for how many tracks are supposed to be shown.
        skip: int
           Number of tracks that are skipped to be shown.

        Returns
        -------
        List[Release]
            All the singles/eps/albums/podcasts (depends how you set the parameters) that are available.
        """
        releases = []
        for release in self.http.get_all_releases(singles=singles, eps=eps, albums=albums, podcasts=podcasts, limit=limit, skip=skip)['results']:
            releases.append(Release(http=self.http, **release))
        return releases

    def get_all_tracks(self, *, limit: int = None, skip: int = None) -> List[Track]:
        """Retrieves every track the client can access.

        Parameters
        ----------
        limit: int
           Limit for how many tracks are supposed to be shown.
        skip: int
           Number of tracks that are skipped to be shown.

        Returns
        -------
        List[Track]
            All the tracks that are available.
        """
        tracks = []
        for track in self.http.get_all_tracks(limit=limit, skip=skip)['results']:
            tracks.append(Track(**track))
        return tracks

    def get_all_artists(self, *, year: int = None, limit: int = None, skip: int = None) -> List[Artist]:
        """Retrieves every artist the client can access.

        Parameters
        ----------
        year: int
           Artists from the year specified that are to be shown.
        limit: int
           Limit for how many artists are supposed to be shown.
        skip: int
           Number of artists that are skipped to be shown.

        Returns
        -------
        List[Artist]
            All the artists that are available.
        """
        artists = []
        for artist in self.http.get_all_artists(year=year, limit=limit, skip=skip)['results']:
            artists.append(Artist(http=self.http, **artist))
        return artists

    def get_all_playlists(self, *, limit: int = None, skip: int = None) -> List[Playlist]:
        """Retrieves every playlist the client can access.

        Parameters
        ----------
        limit: int
           Limit for how many playlists are supposed to be shown.
        skip: int
           Number of playlists that are skipped to be shown.

        Raises
        ------
        Unauthorized
            The client isn't signed in.

        Returns
        -------
        List[Playlist]
           All the playlists that the account has.
        """
        playlists = []
        for playlist in self.http.get_all_playlists(limit=limit, skip=skip)['results']:
            playlists.append(Playlist(http=self.http, **playlist))
        return playlists

    def get_browse_entries(self, *, types: List[str] = None, genres: List[str] = None, tags: List[str] = None, limit: int = None, skip: int = None) -> List[BrowseEntry]:
        # I can't think of a better way to name this function...
        """
        Check `connect.Client.browse_filters` for filters that are needed to be used on the function's parameters.

        Parameters
        ----------
        types: List[str]
            Browse entries types that the API should get.
        genres: List[str]
            Browse entries genres that the API should look for.
        tags: List[str]
            Browse entries tags that the API should look for.
        limit: int
            The limit for how many releases are supposed to be shown.
        skip: int
            Number of releases that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any releases.

        Returns
        -------
        List[BrowseEntry]
            List of browse entries that the API could find with the given filters.
        """
        entries = []
        for entry in self.http.get_browse_entries(types=types, genres=genres, tags=tags, limit=limit, skip=skip)['results']:
            entries.append(BrowseEntry(**entry))
        if not entries:
            raise NotFound('No browse entry was found.')
        else:
            return entries

    def search_release(self, term: str, *, limit: int = None, skip: int = None) -> List[Release]:
        """Searches for a release.

        Parameters
        ----------
        term: str
           The release name that is searched.
        limit: int
           Limit for how many releases are supposed to be shown.
        skip: int
           Number of releases that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any releases.

        Returns
        -------
        List[Release]
            List of releases that the API could find.
        """
        releases = []
        for release in self.http.request('GET', f'{self.http.RELEASE}?fuzzyOr=title,{quote(term)},renderedArtists,{quote(term)}&limit={limit}&skip={skip}')['results']:
            releases.append(Release(http=self.http, **release))
        if not releases:
            raise NotFound('No release was found.')
        else:
            return releases

    def search_release_advanced(self, title: str, artists: str, *, limit: int = None, skip: int = None) -> List[Release]:
        """Searches for a release in a more advanced way.

        Parameters
        ----------
        title: str
           The release title that is searched.
        artists: str
           The release artists that are searched.
        limit: int
           Limit for how many releases are supposed to be shown.
        skip: int
           Number of releases that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any releases.

        Returns
        -------
        List[Release]
            List of releases that the API could find.
        """
        releases = []
        for release in self.http.request('GET', f'{self.http.RELEASE}?fuzzy=title,{quote(title)},renderedArtists,{quote(artists)}&limit={limit}&skip={skip}')['results']:
            releases.append(Release(http=self.http, **release))
        if not releases:
            raise NotFound('No release was found.')
        else:
            return releases

    def search_track(self, term: str, *, limit: int = None, skip: int = None) -> List[Track]:
        """Searches for a track.

        Parameters
        ----------
        term: str
           The track name that is searched.
        limit: int
           Limit for how many tracks are supposed to be shown.
        skip: int
           Number of tracks that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any tracks.

        Returns
        -------
        List[Track]
            List of tracks that the API could find.
        """
        tracks = []
        for track in self.http.request('GET', f'{self.http.TRACK}?fuzzyOr=title,{quote(term)},artistsTitle,{quote(term)}&limit={limit}&skip={skip}')['results']:
            tracks.append(Track(**track))
        if not tracks:
            raise NotFound('No track was found.')
        else:
            return tracks

    def search_track_advanced(self, title: str, artists: str, *, limit: int = None, skip: int = None) -> List[Track]:
        """Searches for a track in a more advanced way.

        Parameters
        ----------
        title: str
           The track title that is searched.
        artists: str
           The track artists that are searched.
        limit: int
           Limit for how many tracks are supposed to be shown.
        skip: int
           Number of tracks that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any tracks.

        Returns
        -------
        List[Track]
            List of tracks that the API could find.
        """
        tracks = []
        for track in self.http.request('GET', f'{self.http.TRACK}?fuzzy=title,{quote(title)},artistsTitle,{quote(artists)}&limit={limit}&skip={skip}')['results']:
            tracks.append(Track(**track))
        if not tracks:
            raise NotFound('No track was found.')
        else:
            return tracks

    def search_artist(self, term: str, *, year: int = None, limit: int = None, skip: int = None) -> List[Artist]:
        """Searches for a artist.

        Parameters
        ----------
        term: str
           The artist name that is searched.
        year: int
           The artists from the year specified that are to be shown.
        limit: int
           Limit for how many artists are supposed to be shown.
        skip: int
           Number of artists that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any artists.

        Returns
        -------
        List[Artist]
            List of artists that the API could find.
        """
        artists = []
        base = f'{self.http.ARTIST}?limit={limit}&skip={skip}&fuzzyOr=name,{quote(term)}'
        if year:
            base = f'{base},year,{year}'
        for artist in self.http.request('GET', base)['results']:
            artists.append(Artist(http=self.http, **artist))
        if not artists:
            raise NotFound('No artist was found.')
        else:
            return artists

    def search_playlist(self, term: str, *, limit: int = None, skip: int = None) -> List[Playlist]:
        """Searches for a playlist.

        Parameters
        ----------
        term: str
           The playlist name that is searched.
        limit: int
           Limit for how many playlists are supposed to be shown.
        skip: int
           Number of playlists that are skipped to be shown.

        Raises
        ------
        Unauthorized
            The client isn't signed in.
        NotFound
            The client couldn't find any playlists.

        Returns
        -------
        List[Playlist]
            List of playlists that the API could find.
        """
        playlists = []
        for playlist in self.http.request('GET', f'{self.http.PLAYLIST}?fuzzyOr=name,{quote(term)}&limit={limit}&skip={skip}')['results']:
            playlists.append(Playlist(http=self.http, **playlist))
        if not playlists:
            raise NotFound('No playlist was found.')
        else:
            return playlists
