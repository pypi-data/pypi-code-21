import random
from datetime import date, timedelta
from itertools import chain

from pyorderby import orderby

from ..cache import *
from ..constants import TimeRange, AudioFeature


class RecommenderMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @db_session
    def fetch_playlists(self):
        results = chain(
            self.user_playlists('particledetector').iterall(),
            self.user_playlists('thesoundsofspotify').iterall()
        )

        for playlist in results:
            if not Playlist.exists(id=playlist.id):
                Playlist.from_dict(playlist)

    @db_session
    def fetch_user_top(self, time_range):
        self.user.top_artists.clear()
        disliked_artists = set(self.user.disliked_artists.id.distinct().keys())
        for artist in self.current_user_top_artists(limit=50, time_range=time_range).iterall():
            if artist.id in disliked_artists:
                continue

            if Artist.exists(id=artist.id):
                self.user.top_artists.add(Artist[artist.id])
            else:
                self.user.top_artists.add(Artist.from_dict(artist))

        self.user.top_genres = self.user.top_artists.genres.distinct().keys() - self.user.disliked_genres
        self.user.top_expires_at = date.today() + timedelta(days=1)

    @db_session
    def genre_playlist(self, genre, popularity=Playlist.Popularity.SOUND):
        return Playlist.get(genre=genre, popularity=Playlist.Popularity(popularity).value)

    @db_session
    def top_artists(self, time_range=TimeRange.SHORT_TERM):
        if self.user.top_expired:
            self.fetch_user_top(time_range)

        return self.user.top_artists

    @db_session
    def top_genres(self, limit=10, time_range=TimeRange.SHORT_TERM):
        if self.user.top_expired:
            self.fetch_user_top(time_range)

        genres = self.user.top_genres
        return genres.select().without_distinct().random(limit) if limit else genres.copy()

    def order_by(self, features, tracks):
        audio_features = self.audio_features(tracks=tracks)
        if isinstance(features, AudioFeature):
            features = features.value

        return sorted(audio_features, key=orderby(features))

    def fill_with_related_artists(self, artists, limit=5):
        artists = set(artists)
        while len(artists) < limit:
            related_artists = self.artist_related_artists(random.choice(list(artists)))

            related_artists_limit = random.randint(1, limit - len(artists))
            artists |= {a.id for a in random.sample(related_artists.artists, related_artists_limit)}

        return artists

    @db_session
    def recommend_by_top_artists(self, artist_limit=2, track_limit=50, use_related=True, features_order=None, time_range=TimeRange.SHORT_TERM, **kwargs):
        """Get a list of recommended songs.

        Returns:
            list: List of tracks
        """

        artists = self.top_artists(time_range=time_range).select().without_distinct().random(artist_limit)
        artists = self.fill_with_related_artists([a.id for a in artists])

        tracks = self.recommendations(seed_artists=artists, limit=track_limit, **kwargs)

        if features_order:
            tracks = self.order_by(features_order, tracks)

        return tracks

    @db_session
    def dislike_artist(self, artist):
        if isinstance(artist, str):
            artist = get(a for a in Artist if a.id == artist or a.name == artist)
        elif isinstance(artist, dict):
            artist = Artist.get(artist.id) or Artist.from_dict(artist)

        self.user.dislike(artist=artist)

    @db_session
    def dislike_genre(self, genre):
        if isinstance(genre, str):
            genre = genre.lower()
            genre = Genre.get(name=genre) or Genre(name=genre)

        self.user.dislike(genre=genre)
