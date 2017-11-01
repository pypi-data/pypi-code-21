#!/usr/bin/env python

"""
Logitech Media Server client.

Provides a client to interact with the lower level Logitech Media Server (LMS)
command line interface (CLI).
"""

from collections import OrderedDict
import re
from telnetlib import Telnet
import time
from urllib import parse


class LMSClient(object):
    """A client for the Logitech Media Server (LMS) command line interface."""

    ACTION_TYPE_ADD = 'add'
    ACTION_TYPE_LOAD = 'load'
    ACTION_TYPES = (
        ACTION_TYPE_ADD,
        ACTION_TYPE_LOAD,
    )
    ITEM_TYPE_ALBUM = 'album'
    ITEM_TYPE_CONTRIBUTOR = 'contributor'
    ITEM_TYPE_TRACK = 'track'
    ITEM_TYPES = (
        ITEM_TYPE_ALBUM,
        ITEM_TYPE_CONTRIBUTOR,
        ITEM_TYPE_TRACK,
    )

    # These numeric values correspond directly with the values
    # returned from LMS.
    SHUFFLE_OFF = 0
    SHUFFLE_SONGS = 1
    SHUFFLE_ALBUMS = 2

    REPEAT_OFF = 0
    REPEAT_SONG = 1
    REPEAT_PLAYLIST = 2

    def __init__(self, host, port=9090, default_player_id=None):
        """Initialize the client."""
        self.host = host
        self.port = port
        self.default_player_id = default_player_id
        self.client = Telnet()

    def connect(self, username=None, password=None):
        """
        Connect to host via telnet client on specified port.

        Provide login credentials if provided.
        """
        self.client.open(self.host, self.port)

        if username and not password:
            raise AssertionError(
                'You provided a username, but no password. Please provide '
                'both or none of them.'
            )
        if password and not username:
            raise AssertionError(
                'You provided a password, but no username. Please provide '
                'both or none of them.'
            )
        if username and password:
            assert isinstance(username, str), (
                'The `username` must be a string.'
            )
            assert isinstance(password, str), (
                'The `password` must be a string.'
            )
            self.send('login {username} {password}'.format(
                username=parse.quote(username),
                password=parse.quote(password)
            ))

    def disconnect(self):
        """Disconnect from host."""
        self.send('exit')
        self.client.close()

    def send(self, command):
        """Send a command to the LMS and return the response."""
        formatted_command = bytes('%s\n' % command, 'utf-8')
        self.client.write(formatted_command)
        response = self.client.read_until(b'\n')
        return response.decode('utf-8').strip()

    def get_players(self):
        """Get information about all connected players."""
        player_count = self.send('player count ?').split(' ').pop()
        response = self.send(
            'players 0 {}'.format(player_count)
        ).split(' ')[4:]
        response = [parse.unquote(item) for item in response]
        player = None
        players = []
        for item in response:
            # Extract info from response item.
            parts = item.split(':')
            key = parts.pop(0)
            value = ':'.join(parts)
            # Decide whether this item is about a new player.
            if key == 'playerindex':
                # If we have a player already, add this to the list of players.
                if player:
                    players.append(player)
                # Start collecting data for a new player.
                player = {}
            # Add info about player.
            player[key] = value

        return players

    def change_player_id(self, player_id):
        """Change the default player ID."""
        self.default_player_id = player_id

    def get_player_name(self, player_id=None):
        """Get the player name."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id
        # Query LMS for player name.
        response = self.send('{} name ?'.format(player_id))
        return parse.unquote(response.split(' ').pop())

    def get_volume_level(self, player_id=None):
        """Get the current volume level."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id
        # Query LMS for volume level.
        response = self.send('{} mixer volume ?'.format(player_id))
        level = parse.unquote(response.split(' ').pop())
        if level == '?':
            raise ValueError(
                'Something is wrong. LMS returned "{}" as the volume level. '
                'This might be because the player ({}) you\'re trying to '
                'control is not connected to LMS.'.format(
                    level,
                    player_id
                )
            )
        try:
            level = float(level)
        except ValueError:
            raise ValueError(
                'Somethings is wrong. LMS returned "{}" as the volume level. '
                'Check the health of your LMS.'.format(level)
            )
        return level

    def change_volume(self, amount, player_id=None):
        """Change the volume by the given amount."""
        # Make sure amount is numeric.
        try:
            amount = float(amount)
        except:
            raise ValueError(
                'When changing volume, the `amount` has to be a numeric '
                'value. `{}` was given.'
            )
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id
        # Change volume and return new volume level.
        self.send('{} mixer volume {}'.format(
            player_id,
            '{}{}'.format('-' if amount < 0 else '+', abs(amount))
        ))
        return self.get_volume_level(player_id)

    def set_volume(self, amount, player_id=None):
        """Set the volume at a specific amount."""
        try:
            amount = float(amount)
        except:
            raise ValueError(
                'When changing volume, the `amount` has to be a numeric '
                'value. `{}` was given.'
            )
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id
        # Set volume and return new volume level.
        self.send('{} mixer volume {}'.format(player_id, amount))
        return self.get_volume_level(player_id)


    def toggle_mute(self, player_id=None):
        """Toggle mute for the player."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id
        # Toggle mute.
        self.send('{} mixer muting toggle'.format(player_id))
        return self.get_volume_level(player_id)

    def get_now_playing(self, player_id=None):
        """Get information about what's playing at the moment."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id
        # Query LMS for data.
        data = {}
        for key in [
            'artist',
            'album',
            'current_title',
            'mode',
            'remote',
            'title',
        ]:
            response = self.send('{} {} ?'.format(player_id, key))
            data[key] = parse.unquote(response.split(' ').pop())
        data['remote'] = int(data['remote'])
        return data

    def get_contributor_albums(self, contributor_id):
        """Return the first 1000 albums by a contributor."""
        # Make sure we know what to do.
        assert type(contributor_id) is int, '`contributor_id` must be an int.'
        # Get data from LMS.
        command = 'albums 0 1000 artist_id:%i' % contributor_id
        response = self.send(command).split(' ')[4:]
        # Parse response into something a bit more readable.
        data = [
            parse.unquote(x).split(':') for
            x in response if
            not parse.unquote(x).startswith('count:')
        ]
        # Parse data into albums.
        albums = []
        album = None
        for entry in data:
            key = entry.pop(0)
            value = ':'.join(entry)
            # Every time we hit an 'id' key, we know it's a new album.
            if key == 'id':
                if album:
                    albums.append(album)
                album = {
                    'id': int(value),
                    'title': '(unknown album)',
                }
            else:
                if key == 'album':
                    album.update({
                        'title': value,
                    })
        albums.append(album)
        # Sort albums.
        albums = sorted(albums, key=lambda album: album.get('title'))
        return albums

    def get_album_tracks(self, album_id):
        """Return the first 1000 tracks of an album."""
        # Make sure we know what to do.
        assert type(album_id) is int, '`album_id` must be an int.'
        # Get data from LMS.
        command = 'tracks 0 1000 album_id:%i tags:t' % album_id
        response = self.send(command).split(' ')[5:]
        # Parse response into something a bit more readable.
        data = [
            parse.unquote(x).split(':') for
            x in response if
            not parse.unquote(x).startswith('count:')
        ]
        # Parse data into tracks.
        tracks = []
        track = None
        for entry in data:
            key = entry.pop(0)
            value = ':'.join(entry)
            # Every time we hit an 'id' key, we know it's a new track.
            if key == 'id':
                if track:
                    tracks.append(track)
                track = {
                    'id': int(value),
                    'title': '(unknown track)',
                    'tracknum': 0,
                }
            else:
                if key == 'tracknum':
                    value = int(value)
                track.update({
                    key: value,
                })
        tracks.append(track)
        # Reverse list as default, as it seems tracks are returned from LMS in
        # reverse order. This is to help for albums with tracks without
        # tracknum, but where the order is somehow guessed by the LMS scanner
        # at import time (e.g. by file name).
        tracks.reverse()
        # Sort tracks.
        tracks = sorted(tracks, key=lambda track: track.get('tracknum'))
        return tracks

    def get_random_album(self):
        """Return a random album."""
        # Get data from LMS.
        command = 'albums 0 1 sort:random'
        response = self.send(command).split(' ')[4:]
        # Parse response into something a bit more readable.
        data = [
            parse.unquote(x).split(':', 1) for
            x in response if
            not parse.unquote(x).startswith('count:')
        ]
        # Turn data into a dict.
        data = {
            k: v for [k, v] in data
        }
        # Make sure the ID is a proper integer.
        data['id'] = int(data.get('id'))
        return data

    def get_most_recent_albums(self):
        """Return the 100 most recently added albums."""
        # Get data from LMS.
        command = 'albums 0 100 sort:new tags:la'
        response = self.send(command).split(' ')[4:]
        # Parse response into something a bit more readable.
        data = [
            parse.unquote(x).split(':') for
            x in response if
            not parse.unquote(x).startswith('count:')
        ]
        # Parse data into albums.
        albums = []
        album = None
        for entry in data:
            key = entry.pop(0)
            value = ':'.join(entry)
            # Every time we hit an 'id' key, we know it's a new album.
            if key == 'id':
                if album:
                    albums.append(album)
                album = {
                    'id': int(value),
                    'title': '(unknown album)',
                }
            else:
                if key == 'album':
                    album.update({
                        'title': value,
                    })
                if key == 'artist':
                    album.update({
                        'artist': value,
                    })
        albums.append(album)
        return albums

    def get_favorites(self, item_id=None):
        """Get a favorites listing, with support for hierarchies."""
        command = 'favorites items 0 1000'
        if item_id:
            command += ' item_id:{}'.format(parse.quote(str(item_id)))
        response = self.send(command)
        data = [parse.unquote(part) for part in response.split(' ')]
        items = []
        item = None
        if item_id == '7':
            raise Exception(data)
        while data:
            entry = parse.unquote(data.pop(0)).split(':')
            key = entry.pop(0)
            value = ':'.join(entry)
            # New items occur when the key is `id`.
            if key == 'id':
                # Append current item to list of items and create a new item.
                if item:
                    # Ignore item if it's the mysqueezebox.com favorites, as we
                    # don't know how to handle this item.
                    if 'mysqueezebox.com' not in item.get('name'):
                        items.append(item)
                # All items are expected to have the `hasitems` property.
                item = {
                    'hasitems': 0
                }
                # Item `id`s at the root level has some sort of hash before
                # the actual ID. Remove this.
                if not item_id:
                    value = value.split('.')[1]
                item[key] = value
            # Skip non-ID entries until we have an item (i.e. found an
            # `id` entry).
            if item:
                # Normalize titles and names.
                if key == 'title':
                    key = 'name'
                # Turn numeric values into numbers.
                if key in ['hasitems']:
                    value = int(value)
                # Add the property to the item.
                item[key] = value
        # Append last item and return them all. Ignore last item if it's the
        # mysqueezebox.com favorites, as we don't know how to handle
        # this item.
        if 'mysqueezebox.com' not in item.get('name'):
            items.append(item)
        return items

    def load_favorite(self, item_id, player_id=None):
        """Play a favorite by its ID."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        # Construct and send the command.
        command = '{} favorites playlist play item_id:{}'.format(
            player_id,
            item_id
        )
        self.send(command)

    def queue_favorite(self, item_id, player_id=None):
        """Add a favorite to the playlist by its ID."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        # Construct and send the command.
        command = '{} favorites playlist add item_id:{}'.format(
            player_id,
            item_id
        )
        self.send(command)

    def search(self, query):
        """Search the LMS media library for items matching the query."""
        # Construct the command query and extract the reponse without leading
        # command.
        command = 'search 0 100 '
        term = parse.quote('term:')
        response = self.send('%s%s%s' % (
            command,
            term,
            parse.quote(query)
            ))[len(command + term + query) + 1:]
        # Parse reponse data into a more sane format.
        raw_data = response.split(' ')
        data = {
            self.ITEM_TYPE_ALBUM: [],
            self.ITEM_TYPE_CONTRIBUTOR: [],
            self.ITEM_TYPE_TRACK: [],
        }
        while raw_data:
            entry = parse.unquote(raw_data.pop(0)).split(':')
            key = entry.pop(0)
            value = ':'.join(entry)
            if key == 'album_id':
                album_id = int(value)
                entry = parse.unquote(raw_data.pop(0)).split(':')
                key = entry.pop(0)
                album_name = ':'.join(entry)
                data[self.ITEM_TYPE_ALBUM].append((album_id, album_name))
            if key == 'contributor_id':
                contributor_id = int(value)
                entry = parse.unquote(raw_data.pop(0)).split(':')
                key = entry.pop(0)
                contributor_name = ':'.join(entry)
                data[self.ITEM_TYPE_CONTRIBUTOR].append((
                    contributor_id,
                    contributor_name,
                ))
            if key == 'track_id':
                track_id = int(value)
                entry = parse.unquote(raw_data.pop(0)).split(':')
                key = entry.pop(0)
                track_name = ':'.join(entry)
                data[self.ITEM_TYPE_TRACK].append((track_id, track_name))

        return data

    def play_pause(self, player_id=None):
        """Play/pause a player."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        # Toggle pause.
        self.send('%s pause' % parse.quote(player_id))

    def handle_item_by_type_and_id(
        self,
        action_type,
        item_type,
        item_id,
        player_id=None
    ):
        """
        Handle a content type by its ID.

        E.g. `ALBUM` with `id=2811` -- with the appropriate action (add/load).
        """
        # Make sure we know what to do.
        assert player_id or self.default_player_id, 'Don\'t know which ' \
            'player to load item into.'
        assert action_type in self.ACTION_TYPES, '%s is not a known ' \
            'action type.'
        assert item_type in self.ITEM_TYPES, '%s is not a known ' \
            'item type.' % item_type
        assert type(item_id) is int, 'Supplied item_id, %s, is not ' \
            'an integer.' % str(item_id)

        # Fix inconsistency quirk around artist/contributor naming in LMS CLI.
        if item_type == self.ITEM_TYPE_CONTRIBUTOR:
            item_type = 'artist'

        # Send command.
        self.send('%s playlistcontrol cmd:%s %s_id:%i' % (
            player_id or self.default_player_id,
            action_type,
            item_type,
            item_id,
        ))

    def add_item_by_type_and_id(self, item_type, item_id, player_id=None):
        """Add a content type by its ID. E.g. `ALBUM` with `id=2811`."""
        self.handle_item_by_type_and_id(
            self.ACTION_TYPE_ADD,
            item_type,
            item_id,
            player_id
        )

    def load_item_by_type_and_id(self, item_type, item_id, player_id=None):
        """Load a content type by its ID. E.g. `ALBUM` with `id=2811`."""
        self.handle_item_by_type_and_id(
            self.ACTION_TYPE_LOAD,
            item_type,
            item_id,
            player_id
        )

    def add_album_by_id(self, album_id, player_id=None):
        """Load an album by its ID."""
        self.load_item_by_type_and_id(
            self.ITEM_TYPE_ALBUM,
            album_id,
            player_id
        )

    def add_contributor_by_id(self, contributor_id, player_id=None):
        """Load a contributor by its ID."""
        self.load_item_by_type_and_id(
            self.ITEM_TYPE_CONTRIBUTOR,
            contributor_id,
            player_id
        )

    def add_track_by_id(self, track, player_id=None):
        """Load a track by its ID."""
        self.load_item_by_type_and_id(
            self.ITEM_TYPE_TRACK,
            track,
            player_id
        )

    def load_album_by_id(self, album_id, player_id=None):
        """Load an album by its ID."""
        self.load_item_by_type_and_id(
            self.ITEM_TYPE_ALBUM,
            album_id,
            player_id
        )

    def load_contributor_by_id(self, contributor_id, player_id=None):
        """Load a contributor by its ID."""
        self.load_item_by_type_and_id(
            self.ITEM_TYPE_CONTRIBUTOR,
            contributor_id,
            player_id
        )

    def load_track_by_id(self, track, player_id=None):
        """Load a track by its ID."""
        self.load_item_by_type_and_id(
            self.ITEM_TYPE_TRACK,
            track,
            player_id
        )

    def get_current_playlist_track_count(self, player_id=None):
        """Get the amount of tracks on the current playlist of a player."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id
        # Construct the command, get a response and return the value.
        command = '%s playlist tracks' % parse.quote(player_id)
        response = self.send('%s ?' % (
            command,
        ))[len(command) + 1:]
        return int(response.strip())

    def get_current_track_playlist_index(self, player_id=None):
        """Get the playlist index of the current track of a player."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id
        # Construct the command, get a response and return the value.
        command = '%s playlist index' % parse.quote(player_id)
        response = self.send('%s ?' % (
            command,
        ))[len(command) + 1:]
        return int(response.strip())

    def get_current_playlist_tracks(self, player_id=None):
        """Get the tracks on the current playlist of a player."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        # Get playlist track count, to know how many tracks to ask for.
        track_count = self.get_current_playlist_track_count(player_id)

        # Get playlist index of current track.
        current_track_index = self.get_current_track_playlist_index(player_id)

        # Construct command and get a response.
        command = '%s status 0 %i' % (
            parse.quote(player_id),
            track_count,
        )
        response = self.send(command)[len(command) + 1:]

        # Parse the response into useful data.
        data = [parse.unquote(entry) for entry in response.split(' ')]

        # Remove unwanted data entries.
        # TODO: There must be a better way to query for the current playlist
        # without getting all this useless information at the same time.
        data = [entry for entry in data if not entry.split(':')[0] in [
            'player_name',
            'player_connected',
            'player_ip',
            'power',
            'signalstrength',
            'mode',
            'time',
            'rate',
            'duration',
            'can_seek',
            'mixer volume',
            'playlist repeat',
            'playlist shuffle',
            'playlist mode',
            'seq_no',
            'playlist_cur_index',
            'playlist_timestamp',
            'playlist_tracks',
            'digital_volume_control',
            'sync_master',
            'sync_slaves',
            'genre',
            'remote',
            'current_title',
            'remoteMeta',
        ]]

        # Extract track info from data.
        tracks = []
        track = None
        for entry in data:
            # Split entry into its parts.
            parts = entry.split(':')
            key = parts[0]
            value = ' '.join(parts[1:])

            # Clean up integer fields.
            if key in ['playlist index', 'id']:
                value = int(value)

            # Start a new track at each playlist index.
            if key == 'playlist index':
                if track is not None:
                    tracks.append(track)
                track = {}

            # Add entry data to track.
            track[key] = value

        # Add the final track to listing.
        tracks.append(track)

        return tracks

    def play_playlist_track_index(self, index, player_id=None):
        """Play the playlist track at the given index."""
        # Make sure we got a proper index.
        assert type(index) is int, 'Playlist index must be an integer.'

        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        # Construct and send the command.
        command = '%s playlist index %i' % (
            parse.quote(player_id),
            index,
        )
        response = self.send(command)

    def play_next(self, player_id=None):
        """Skip to next track in playlist."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        # Construct and send the command.
        command = '{} playlist index +1'.format(parse.quote(player_id))
        response = self.send(command)

    def play_previous(self, player_id=None):
        """Skip to previous track in playlist."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        # Construct and send the command.
        command = '{} playlist index -1'.format(parse.quote(player_id))
        response = self.send(command)

    def get_shuffle_state(self, player_id=None):
        """Get the current paylist shuffle state."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        command = '{} playlist shuffle ?'.format(parse.quote(player_id))
        return int(self.send(command)[len(command) - 1:])

    def toggle_shuffle(self, new_state=None, player_id=None):
        """
        Toggle the shuffle state.

        Cycle to next value if no new value is provided.
        """
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        # Cycle to next state.
        if new_state is None:
            command = '{} playlist shuffle'.format(parse.quote(player_id))
        elif new_state in [0, 1, 2]:
            command = '{} playlist shuffle {}'.format(
                parse.quote(player_id),
                new_state
            )
        else:
            raise ValueError(
                '{} is not a valid shuffle state.'.format(new_state)
            )
        self.send(command)

    def get_repeat_state(self, player_id=None):
        """Get the current paylist repeat state."""
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        command = '{} playlist repeat ?'.format(parse.quote(player_id))
        return int(self.send(command)[len(command) - 1:])

    def toggle_repeat(self, new_state=None, player_id=None):
        """
        Toggle the repeat state.

        Cycle to next value if no new value is provided.
        """
        # Decide which player to query.
        if not player_id:
            player_id = self.default_player_id

        # Cycle to next state.
        if new_state is None:
            command = '{} playlist repeat'.format(parse.quote(player_id))
        elif new_state in [0, 1, 2]:
            command = '{} playlist repeat {}'.format(
                parse.quote(player_id),
                new_state
            )
        else:
            raise ValueError(
                '{} is not a valid repeat state.'.format(new_state)
            )
        self.send(command)
