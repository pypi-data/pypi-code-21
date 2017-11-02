#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
from datetime import datetime, timedelta
import getopt
import itertools
import json
import locale
import os
import time
import sys

from cursebox.lms import LMSClient


VERSION = '1.0.6.1'

DEFAULT_CONFIG_PATH = '~/.cursebox.conf'
DEFAULT_CONFIG = {
    'server': {
        'password': None,
        'port': 9090,
        'username': None,
        'host': 'localhost',
    },
    'selected_player': {
        'id': '00:00:00:00:00:00',
        'name': 'My Squeezebox',
    }
}

ERROR_MANDATORY_OPTIONS_MISSING = 2
ERROR_TOO_MANY_ARGUMENTS = 3
ERROR_UNKNOWN_ARGUMENT = 4
ERROR_CONFIG_FILE_ALREADY_EXISTS = 5
ERROR_CONFIG_FILE_NOT_FOUND = 6

BACKSPACE_CODES = [curses.KEY_BACKSPACE, 127,]

class Cursebox():
    """
    Cursebox is a curses based interface for controlling Squeezeboxes via the
    Logitech Media Server CLI.
    """
    SEARCH_DELAY = 250  # In milliseconds.
    def __init__(self, window):
        """
        Cursebox should be instantiated with a curses window.
        """
        self.window = window
        self.search_results_cache = {}
        self.client = None
        self.root = os.path.dirname(__file__)

    def get_wch(self):
        """
        Wrapper around `curses.window.cet_wch()`.

        This one doesn't raise an error in nodelay mode.
        """
        try:
            return self.window.get_wch()
        except curses.error:
            return None

    def clear_slate(self, from_row=1):
        """
        Clear the entire window from a given row.
        """
        self.window.move(from_row, 0)
        self.window.clrtobot()

    def render_list(self, items, first_line, highlight=None):
        """
        Render a list of items, including an optional hightlight.
        """
        line = first_line
        for item in items:
            if (
                type(highlight) is int and
                highlight % len(items) == line - first_line
            ):
                style = curses.A_REVERSE
            else:
                style = 0
            self.window.addstr(
                line,
                0,
                item,
                style
            )
            line = line + 1


    @property
    def allow_play_from_the_top(self):
        """Find out whether it's 'play from the top' should be an option."""
        now_playing_data = self.client.get_now_playing()
        if now_playing_data.get('mode') != 'stop':
            return False
        current_track = self.client.get_current_track_playlist_index()
        current_playlist_tracks = self.client.get_current_playlist_tracks()
        return current_track + 1 == len(current_playlist_tracks)

    def perform_search(self, query):
        """
        Perform a search in LMS and cache all results, for better performance.
        """
        if query in self.search_results_cache.keys():
            results = self.search_results_cache.get(query)
        else:
            results = self.client.search(query)
            self.search_results_cache[query] = results
        return results

    def show_results(self, query, item_type, highlight=None):
        """
        Show a list of search results, optionally with a highligted item.
        """
        assert item_type in self.client.ITEM_TYPES, 'Unknown search item ' \
            'type "%s"' % item_type
        self.window.clrtobot()
        self.window.refresh()
        if query:
            results = self.perform_search(query)
            if results.get(item_type):
                items = results.get(item_type)
                y, x = self.window.getmaxyx()
                self.render_list(
                    [i[1] for i in items[0:y - 3]],
                    3,
                    highlight
                )
            else:
                self.window.addstr(3, 0, '(nothing found)')

    def start_screen(self):
        """
        Show the start screen.
        """
        self.window.nodelay(1)
        self.clear_slate()
        player_name = self.client.get_player_name()
        volume = self.client.get_volume_level()
        if volume < 0:
            volume = 'Muted'
        else:
            volume = '{}%'.format(volume)
        now_playing_data = self.client.get_now_playing()
        if now_playing_data.get('mode') == 'play':
            if now_playing_data.get('remote'):
                now_playing = now_playing_data.get('current_title')
            else:
                now_playing = now_playing_data.get('title')
                if now_playing_data.get('album'):
                    now_playing = '{} - {}'.format(
                        now_playing,
                        now_playing_data.get('album'),
                    )
                if now_playing_data.get('artist'):
                    now_playing = '{} - {}'.format(
                        now_playing,
                        now_playing_data.get('artist'),
                    )
        else:
            now_playing = ''
        shuffle_state = self.client.get_shuffle_state()
        repeat_state = self.client.get_repeat_state()
        shuffle_label = [
            'Off',
            'Songs',
            'Albums',
        ][shuffle_state]
        repeat_label = [
            'Off',
            'Song',
            'Playlist',
        ][repeat_state]
        line = itertools.count(1)
        self.window.addstr(next(line), 0, '')
        if now_playing:
            self.window.addstr(next(line), 0, 'Now playing: {}'.format(
                now_playing
            ))
        self.window.addstr(next(line), 0, 'Player: {}'.format(player_name))
        self.window.addstr(next(line), 0, 'Volume: {}'.format(volume))
        self.window.addstr(next(line), 0, '[R]epeat: {}  [S]huffle: {}'.format(
            repeat_label,
            shuffle_label
        ))
        self.window.addstr(next(line), 0, '')
        self.window.addstr(next(line), 0, 'Select action:')
        self.window.addstr(
            next(line),
            0,
            '[Space]  {}'.format(
                'Pause' if
                now_playing_data.get('mode') == 'play' else
                'Play'
            )
        )
        if self.allow_play_from_the_top:
            self.window.addstr(next(line), 0, '[G]      Play from the top')
        self.window.addstr(next(line), 0, '[h/l]    Previous/next track')
        self.window.addstr(next(line), 0, '[p]      Show current playlist')
        self.window.addstr(next(line), 0, '[s]      Search')
        self.window.addstr(next(line), 0, '[n]      New music')
        self.window.addstr(next(line), 0, '[f]      Favorites')
        self.window.addstr(next(line), 0, '[r]      Play random album')
        self.window.addstr(next(line), 0, '[j/k]    Descrease/increase volume')
        self.window.addstr(next(line), 0, '[v]      Volume settings')
        self.window.addstr(next(line), 0, '[c]      Change player')
        self.window.addstr(next(line), 0, '[q]      Quit')
        mac_debug = False
        while 1:
            # Get key press.
            c = self.get_wch()
            if c and mac_debug:
                raise Exception('Key: {}, type: {}, ord: {}'.format(
                    c,
                    type(c),
                    ord(c) if type(c) == str else 'N/A'
                ))
            if c == 'D':
                mac_debug = True
            # Play/pause.
            if c == ' ':
                self.client.play_pause()
                # Reload start screen to update now playing info.
                self.start_screen()
                break;
            if c == 'R':
                self.client.toggle_repeat()
                # Reload start screen to update the state.
                self.start_screen()
                break;
            if c == 'S':
                self.client.toggle_shuffle()
                # Reload start screen to update the state.
                self.start_screen()
                break;
            # Play from the top.
            if c == 'G' and self.allow_play_from_the_top:
                self.client.play_playlist_track_index(0)
                self.start_screen()
                break;
            # Skip to previous/next track.
            if c in ['h', 'l']:
                (
                    self.client.play_previous() if
                    c == 'h' else
                    self.client.play_next()
                )
                self.start_screen()
                break
            # Show current playlist.
            elif c == 'p':
                self.current_playlist_screen()
                break
            # Search.
            elif c == 's':
                self.pre_search_screen()
                break
            # New music.
            elif c == 'n':
                self.list_new_music()
                break
            # Favorites.
            elif c == 'f':
                self.list_favorites()
                break
            # Random album.
            elif c == 'r':
                self.play_random_album()
                self.start_screen()
                break
            # Incrase/descrease volume.
            if c in ['j', 'k']:
                step = 2.5
                self.client.change_volume(step if c == 'k' else -step)
                self.start_screen()
                break
            # Change volume.
            elif c == 'v':
                self.volume_screen()
                break
            # Change player.
            elif c == 'c':
                self.player_selection_screen()
                break
            # Quit.
            elif c == 'q':
                self.client.disconnect()
                break
            # Ehh... Dunno.
            else:
                pass
            self.window.refresh()

    def pre_search_screen(self):
        """
        Show the pre search screen, allowing the user to choose the type of
        search to perform.
        """
        self.clear_slate()
        self.window.addstr(2, 0, 'Choose type of search:')
        self.window.addstr(3, 0, '[c]          Contributor (artist)')
        self.window.addstr(4, 0, '[a]          Album')
        self.window.addstr(5, 0, '[t]          Track')
        self.window.addstr(6, 0, '[q]          Quit')
        self.window.addstr(7, 0, '[Backspace]  Return home')
        while 1:
            # Get key press.
            c = self.get_wch()
            # Search by type.
            if c in ('a', 'c', 't'):
                self.search_screen({
                    'a': self.client.ITEM_TYPE_ALBUM,
                    'c': self.client.ITEM_TYPE_CONTRIBUTOR,
                    't': self.client.ITEM_TYPE_TRACK,
                }.get(c))
                break
            # Go back to start.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break
            # Quit.
            elif c == 'q':
                self.client.disconnect()
                break
            # Unknown input.
            else:
                pass

    def volume_screen(self):
        """Change the player volume."""
        volume = self.client.get_volume_level()
        if volume < 0:
            volume = 'Muted'
        else:
            volume = '{}%'.format(volume)
        self.clear_slate()
        self.window.addstr(2, 0, 'Volume: {}'.format(volume))
        self.window.addstr(3, 0, '')
        self.window.addstr(4, 0, '[m]          {}'.format(
            'Unmute' if volume == 'Muted' else 'Mute'
        ))
        self.window.addstr(5, 0, '[j/k]        Descrease/increase volume')
        self.window.addstr(6, 0, '[0-9]        1 = 10%, 2 = 20%, ..., 0 = 100%')
        self.window.addstr(7, 0, '[q]          Quit')
        self.window.addstr(8, 0, '[Backspace]  Return home')
        while 1:
            # Get key press.
            c = self.get_wch()
            # Toggle mute.
            if c == 'm':
                self.client.toggle_mute()
                self.volume_screen()
                break
            # Incrase/descrease.
            if c in ['j', 'k']:
                step = 2.5
                self.client.change_volume(step if c == 'k' else -step)
                self.volume_screen()
                break
            # Fixed 1/10 steps.
            if c in [str(i) for i in range(10)]:
                step = int(c)
                # Make the 0-key turn to 100%.
                if step == 0:
                    self.client.set_volume(100)
                else:
                    self.client.set_volume(step * 10)
                self.volume_screen()
                break
            # Go back to start.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break
            # Quit.
            if c == 'q':
                self.client.disconnect()
                break

    def playlist_action_screen(self, item_type, item_id):
        """
        Show the playlist action screen, allowing the user to play or queue an
        item, or -- for contributors and artists -- go 1 level deeper.
        """
        self.clear_slate()
        self.window.addstr(2, 0, 'Choose what to do:')
        self.window.addstr(3, 0, '[a]         Add to playlist (queue)')
        self.window.addstr(4, 0, '[p]         Play now')
        line = 5
        if item_type == self.client.ITEM_TYPE_ALBUM:
            self.window.addstr(line, 0, '[t]         Select track')
            line = line + 1
        elif item_type == self.client.ITEM_TYPE_CONTRIBUTOR:
            self.window.addstr(line, 0, '[s]         Select album')
            line = line + 1
        self.window.addstr(line + 0, 0, '[q]         Quit')
        self.window.addstr(line + 1, 0, '[Backspace] Return home')
        while 1:
            # Get key press.
            c = self.get_wch()
            # Quit.
            if c == 'q':
                self.client.disconnect()
                break
            # Play immediately.
            elif c == 'p':
                self.client.load_item_by_type_and_id(
                    item_type,
                    item_id
                )
                self.start_screen()
                break
            # Add to playlist.
            elif c == 'a':
                self.client.add_item_by_type_and_id(
                    item_type,
                    item_id
                )
                self.start_screen()
                break
            # For albums, select track
            elif c == 't' and item_type == self.client.ITEM_TYPE_ALBUM:
                self.album_track_screen(item_id)
                break
            # For contributors, select album
            elif c == 's' and item_type == self.client.ITEM_TYPE_CONTRIBUTOR:
                self.contributor_album_screen(item_id)
                break
            # Return home.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break

    def album_track_screen(self, album_id):
        """
        Show the tracks of an album, allowing the user to choose which track to
        queue/play.
        """
        self.clear_slate()
        tracks = self.client.get_album_tracks(album_id)
        self.window.addstr(2, 0, 'Select a track:')
        highlight = None
        self.render_list([t.get('title') for t in tracks], 3, highlight)
        track = None
        while 1:
            # Update selected track.
            if highlight is not None:
                track = tracks[highlight]
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    self.playlist_action_screen(
                        self.client.ITEM_TYPE_TRACK,
                        track.get('id')
                    )
                    break
                self.start_screen()
                break
            # Handle Tab and Shift+Tab properly. These are used for
            # highlighting search result to be played.
            elif c == '\t' or c == 353:
                if highlight is None:
                    highlight = 0 if c == '\t' else -1
                else:
                    highlight = highlight + (1 if c == '\t' else -1)
                # Make sure the highlight index is positive.
                highlight = highlight % len(tracks)
                highlight = highlight + len(tracks)
                highlight = highlight % len(tracks)
                # Render list.
                self.render_list(
                    [t.get('title') for t in tracks],
                    3,
                    highlight
                )
            # Play immediately.
            elif c == 'p':
                if track is not None:
                    self.client.load_item_by_type_and_id(
                        self.client.ITEM_TYPE_TRACK,
                        track.get('id')
                    )
                    self.start_screen()
                    break
            # Add to playlist.
            elif c == 'a':
                if track is not None:
                    self.client.add_item_by_type_and_id(
                        self.client.ITEM_TYPE_TRACK,
                        track.get('id')
                    )
                    self.start_screen()
                    break
            # Return to album action screen.
            elif c in BACKSPACE_CODES:
                self.playlist_action_screen(
                    self.client.ITEM_TYPE_ALBUM,
                    album_id
                )
                break
            # Quit.
            if c == 'q':
                self.client.disconnect()
                break

    def contributor_album_screen(self, contributor_id):
        """
        Show the albums of a contributor, allowing the user to choose which
        album to queue/play.
        """
        self.clear_slate()
        albums = self.client.get_contributor_albums(contributor_id)
        self.window.addstr(2, 0, 'Select an album:')
        highlight = None
        self.render_list([a.get('title') for a in albums], 3, highlight)
        album = None
        while 1:
            # Update album.
            if highlight is not None:
                album = albums[highlight]
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    self.playlist_action_screen(
                        self.client.ITEM_TYPE_ALBUM,
                        album.get('id')
                    )
                    break
                self.start_screen()
                break
            # Handle Tab and Shift+Tab properly. These are used for
            # highlighting search result to be played.
            elif c == '\t' or c == 353:
                if highlight is None:
                    highlight = 0 if c == '\t' else -1
                else:
                    highlight = highlight + (1 if c == '\t' else -1)
                # Make sure the highlight index is positive.
                highlight = highlight % len(albums)
                highlight = highlight + len(albums)
                highlight = highlight % len(albums)
                # Render list.
                self.render_list(
                    [a.get('title') for a in albums],
                    3,
                    highlight
                )
            # Play immediately.
            elif c == 'p':
                if album is not None:
                    self.client.load_item_by_type_and_id(
                        self.client.ITEM_TYPE_ALBUM,
                        album.get('id')
                    )
                    self.start_screen()
                    break
            # Add to playlist.
            elif c == 'a':
                if album is not None:
                    self.client.add_item_by_type_and_id(
                        self.client.ITEM_TYPE_ALBUM,
                        album.get('id')
                    )
                    self.start_screen()
                    break
            # Select track.
            elif c == 't':
                if album is not None:
                    self.album_track_screen(album.get('id'))
                    break
            # Return to contributor action menu.
            elif c in BACKSPACE_CODES:
                self.playlist_action_screen(
                    self.client.ITEM_TYPE_CONTRIBUTOR,
                    contributor_id
                )
                break
            # Quit.
            if c == 'q':
                self.client.disconnect()
                break

    def play_random_album(self):
        """Play a random album."""
        album = self.client.get_random_album()
        self.client.load_item_by_type_and_id(
            self.client.ITEM_TYPE_ALBUM,
            album.get('id')
        )

    def list_new_music(self):
        """Show the most recently added albums."""
        self.clear_slate()
        albums = self.client.get_most_recent_albums()
        self.window.addstr(2, 0, 'Select an album:')
        highlight = None
        items = [
            '{} by {}'.format(
                a.get('title'),
                a.get('artist')
            ) for a in albums
        ]
        y, x = self.window.getmaxyx()
        self.render_list(
            [i for i in items[0:y - 3]],
            3,
            highlight
        )
        album = None
        while 1:
            # Update album.
            if highlight is not None:
                album = albums[highlight]
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    self.playlist_action_screen(
                        self.client.ITEM_TYPE_ALBUM,
                        album.get('id')
                    )
                    break
                self.start_screen()
                break
            # Handle Tab and Shift+Tab properly. These are used for
            # highlighting search result to be played.
            elif c == '\t' or c == 353:
                if highlight is None:
                    highlight = 0 if c == '\t' else -1
                else:
                    highlight = highlight + (1 if c == '\t' else -1)
                y, x = self.window.getmaxyx()
                # Make sure the highlight index is positive.
                highlight = highlight % len(albums)
                highlight = highlight + len(albums)
                highlight = highlight % len(albums)
                # Render list.
                self.render_list(
                    [i for i in items[0:y - 3]],
                    3,
                    highlight
                )
            # Play immediately.
            elif c == 'p':
                if album is not None:
                    self.client.load_item_by_type_and_id(
                        self.client.ITEM_TYPE_ALBUM,
                        album.get('id')
                    )
                    self.start_screen()
                    break
            # Add to playlist.
            elif c == 'a':
                if album is not None:
                    self.client.add_item_by_type_and_id(
                        self.client.ITEM_TYPE_ALBUM,
                        album.get('id')
                    )
                    self.start_screen()
                    break
            # Select track.
            elif c == 't':
                if album is not None:
                    self.album_track_screen(album.get('id'))
                    break
            # Return to start screen.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break
            # Quit.
            if c == 'q':
                self.client.disconnect()
                break

    def list_favorites(self, item_id=None, title=None):
        """Show a favorites listing, with support for hierarchies."""
        self.clear_slate()
        favorites = self.client.get_favorites(item_id)
        # Append sublevel indicator.
        max_length = max([
            len(f.get('name')) for f in favorites
        ])
        for f in favorites:
            if f.get('hasitems') > 0:
                f['original_name'] = f.get('name')
                f['name'] = '{:{}}>'.format(f.get('name'), max_length + 2)
        # Make sure we have a title.
        if not title:
            title = 'Select a favorite'
        self.window.addstr(2, 0, '{}:'.format(title))
        highlight = None
        items = [f.get('name') for f in favorites]
        y, x = self.window.getmaxyx()
        self.render_list(
            [i for i in items[0:y - 3]],
            3,
            highlight
        )
        favorite = None
        while 1:
            # Update favorite.
            if highlight is not None:
                favorite = favorites[highlight]
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    # Show another listing if this favorite has sub items.
                    if favorite.get('hasitems') > 0:
                        self.list_favorites(
                            favorite.get('id'),
                            favorite.get('original_name')
                        )
                    # Show actions for the favorite.
                    else:
                        self.favorite_action_screen(favorite)
                    break
                self.start_screen()
                break
            # Handle Tab and Shift+Tab properly. These are used for
            # highlighting search result to be played.
            elif c == '\t' or c == 353:
                if highlight is None:
                    highlight = 0 if c == '\t' else -1
                else:
                    highlight = highlight + (1 if c == '\t' else -1)
                y, x = self.window.getmaxyx()
                # Make sure the highlight index is positive.
                highlight = highlight % len(favorites)
                highlight = highlight + len(favorites)
                highlight = highlight % len(favorites)
                # Render list.
                self.render_list(
                    [i for i in items[0:y - 3]],
                    3,
                    highlight
                )
            # Play immediately.
            elif c == 'p':
                if favorite is not None and favorite.get('hasitems') == 0:
                    self.client.load_favorite(favorite.get('id'))
                    self.start_screen()
                    break
            # Add to playlist.
            elif c == 'a':
                if favorite is not None and favorite.get('hasitems') == 0:
                    self.client.queue_favorite(favorite.get('id'))
                    self.start_screen()
                    break
            # Return to start screen.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break
            # Quit.
            if c == 'q':
                self.client.disconnect()
                break

    def favorite_action_screen(self, favorite):
        """
        Show the favorite action screen, allowing the user to play or queue a
        favorite.
        """
        self.clear_slate()
        self.window.addstr(2, 0, favorite.get('name'))
        self.window.addstr(3, 0, 'Choose what to do:')
        self.window.addstr(4, 0, '[a]         Add to playlist (queue)')
        self.window.addstr(5, 0, '[p]         Play now')
        self.window.addstr(6, 0, '[q]         Quit')
        self.window.addstr(7, 0, '[Backspace] Return home')
        while 1:
            # Get key press.
            c = self.get_wch()
            # Quit.
            if c == 'q':
                self.client.disconnect()
                break
            # Play immediately.
            elif c == 'p':
                self.client.load_favorite(favorite.get('id'))
                self.start_screen()
                break
            # Add to playlist.
            elif c == 'a':
                self.client.queue_favorite(favorite.get('id'))
                self.start_screen()
                break
            # Return home.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break

    def search_screen(self, item_type):
        """
        Show the search screen, allowing the user to search items of a
        previously specified type.
        """
        label = 'Search {}:'.format(item_type)
        self.clear_slate()
        self.window.addstr(2, 0, label)
        highlight = None
        query = ''
        last_keypress = None
        while 1:
            # Get key press.
            c = self.get_wch()
            # If key is enter, play highligted item (if any) and return home.
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    results = self.search_results_cache.get(query).get(
                       item_type
                    )
                    # Make sure the highlight index is positive.
                    highlight = highlight % len(results)
                    highlight = highlight + len(results)
                    highlight = highlight % len(results)
                    item_id, item_name = results[highlight]
                    self.playlist_action_screen(item_type, item_id)
                    break
                self.start_screen()
                break
            # Handle backspace properly.
            elif c in BACKSPACE_CODES:
                if not query:
                    self.pre_search_screen()
                    break
                query = query[:-1]
                self.window.addstr(2, len(label) + 1, query)
                self.window.clrtoeol()
                highlight = None
                last_keypress = datetime.now()
            # Handle Tab and Shift+Tab properly. These are used for
            # highlighting search result to be played.
            elif c == '\t' or c == 353:
                if highlight is None:
                    highlight = 0 if c == '\t' else -1
                else:
                    highlight = highlight + (1 if c == '\t' else -1)
                # Make sure to update immediately in this case.
                last_keypress = datetime.now() - timedelta(
                    milliseconds=self.SEARCH_DELAY
                )
            # Append key to query if it looks like a character was pressed.
            elif type(c) is str:
                query = query + c
                self.window.addstr(2, len(query) + len(label), c)
                highlight = None
                last_keypress = datetime.now()
            # Some other special key was pressed. Don't really know how to handle
            # these yet.
            else:
                pass
            # Delay search a bit, to improve the find-as-you-type experience.
            if (
                last_keypress and
                datetime.now() - last_keypress >= timedelta(
                    milliseconds=self.SEARCH_DELAY
                )
            ):
                self.show_results(
                    query,
                    item_type,
                    highlight
                )
                last_keypress = None
            self.window.refresh()

    def current_playlist_screen(self):
        """
        Show the current playlist, indicate which track is currently playing,
        and allow the user to Tab navigate tracks, to play another track.
        """
        self.clear_slate()
        current_track = self.client.get_current_track_playlist_index()
        current_playlist_tracks = self.client.get_current_playlist_tracks()
        tracks = [
            (
                (' ♪ %s' % t.get('title')) if
                t.get('playlist index') == current_track else
                (' * %s' % t.get('title'))
            ) for t in current_playlist_tracks
        ]
        self.window.addstr(2, 0, 'Current playlist:')
        highlight = current_track
        self.render_list(tracks, 3, highlight)
        while 1:
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    # Make sure the highlight index is positive.
                    highlight = highlight % len(tracks)
                    highlight = highlight + len(tracks)
                    highlight = highlight % len(tracks)
                    track = tracks[highlight]
                    self.client.play_playlist_track_index(highlight)
                    # Update current track and track listing.
                    current_track = self.client.get_current_track_playlist_index()
                    tracks = [
                        (
                            (' ♪ %s' % t.get('title')) if
                            t.get('playlist index') == current_track else
                            (' * %s' % t.get('title'))
                        ) for t in current_playlist_tracks
                    ]
                    self.render_list(tracks, 3, highlight)
            # Handle Tab and Shift+Tab properly. These are used for
            # highlighting search result to be played.
            elif c == '\t' or c == 353:
                if highlight is None:
                    highlight = 0 if c == '\t' else -1
                else:
                    highlight = highlight + (1 if c == '\t' else -1)
                self.render_list(tracks, 3, highlight)
            # Skip to previous/next track.
            if c in ['h', 'l']:
                (
                    self.client.play_previous() if
                    c == 'h' else
                    self.client.play_next()
                )
                # Update current track and track listing.
                current_track = self.client.get_current_track_playlist_index()
                tracks = [
                    (
                        (' ♪ %s' % t.get('title')) if
                        t.get('playlist index') == current_track else
                        (' * %s' % t.get('title'))
                    ) for t in current_playlist_tracks
                ]
                self.render_list(tracks, 3, highlight)
            # Quit.
            elif c == 'q':
                self.client.disconnect()
                break
            # Return to home.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break


    def player_selection_screen(self):
        """
        List players connected to LMS.

        Allows the user to choose which player to control.
        """
        self.clear_slate()
        players = self.client.get_players()
        menu_items = [
            ' {} {}'.format(
                (
                    'x' if
                    p.get('playerid') == self.client.default_player_id else
                    '*'
                ),
                p.get('name')
            ) for p in players
        ]
        self.window.addstr(2, 0, 'Select a player:')
        idx = 0

        # Find position of currently selected player.
        highlight = None
        for player in players:
            if player.get('playerid') == self.client.default_player_id:
                highlight = idx
            idx += 1

        self.render_list(menu_items, 3, highlight)
        while 1:
            # Get key press.
            c = self.get_wch()
            if type(c) is str and ord(c) in [curses.KEY_ENTER, 10, 13]:
                if highlight is not None:
                    # Make sure the highlight index is positive.
                    highlight = highlight % len(players)
                    highlight = highlight + len(players)
                    highlight = highlight % len(players)
                    player = players[highlight]
                    self.client.change_player_id(player.get('playerid'))
                    self.start_screen()
                    break
            # Handle Tab and Shift+Tab properly. These are used for
            # highlighting search result to be played.
            elif c == '\t' or c == 353:
                if highlight is None:
                    highlight = 0 if c == '\t' else -1
                else:
                    highlight = highlight + (1 if c == '\t' else -1)
                self.render_list(menu_items, 3, highlight)
            # Quit.
            elif c == 'q':
                self.client.disconnect()
                break
            # Return to home.
            elif c in BACKSPACE_CODES:
                self.start_screen()
                break

    def show_splash(self):
        """
        Show a splash screen with the ASCII logo.
        """
        with open(os.path.join(
            self.root,
            './resources/logo.txt'
        )) as f:
            logo_lines = f.readlines()
        line = itertools.count(0)
        for logo_line in logo_lines:
            self.window.addstr(next(line), 0, logo_line)
        next(line)
        self.window.addstr(
            next(line),
            0,
            ' {:^40}'.format('Connecting to LMS...')
        )
        self.window.refresh()

    def start(self, server_name, server_port, username, password, player_id):
        """
        Initialise and connect an LMS client and set up the curses application.
        """
        # Prepare curses window.
        curses.curs_set(0)
        # Show splash screen.
        self.show_splash()
        # Set up LMS client.
        start_time = datetime.now()
        self.client = LMSClient(
            server_name,
            port=server_port,
            default_player_id=player_id
        )
        self.client.connect(username, password)
        # Make sure splash screen is shown for at least 1 second.
        splash_time = datetime.now() - start_time
        if splash_time.seconds == 0:
            time.sleep(1 - splash_time.microseconds / 1000000)
        # Set up window and show correct screen.
        self.clear_slate(0)
        self.window.addstr(0, 0, 'CURSEBOX!')
        # Show player selection if player ID is set. Otherwise, show the
        # start screen.
        if not self.client.default_player_id:
            self.player_selection_screen()
        else:
            self.start_screen()

def usage():
    print( """Usage: cursebox [OPTIONS] [ARG]
Squeezebox and music library control. Make Squeezeboxes great again!

OPTIONS

The following options are recognised:

  -c, --config          Path to configuration file. Optional. Default location
                        is ~/.cursebox.conf
  -s, --server          Hostname of the LMS server to connect to.
  -p, --port            Port of the LMS server to connect to. Optional,
                        defaults to 9090.
  -u  --username        Username used for authentication with LMS. Optional.
  -P  --password        Password used for authentication with LMS. Optional.
  -b, --player_id       ID (MAC address) of the Squeezebox to connect to.
  -h, --help            Show this help message. Obviously optional.

ARGUMENT(S)

Only a single argument (or none at all) is allowed. Can be one of
the following:

  create-config         Create a new default configuration file in
                        ~/.cursebox.conf (if it doesn't already exist).

Prodiving no arguments will simply launch Cursebox.""")

def create_default_config(config_path):
    """
    Creates a new default configuration file.

    At the given path, but only if the file doesn't already exist.
    """
    # Expand path if located in home directory.
    if '~' in config_path:
        config_path = os.path.expanduser(config_path)

    # Make sure there is no existing file on the given path.
    if os.path.exists(config_path):
        print(
            'The file `{}` already exists. Cursebox will not '
            'overwrite this.'.format(
                config_path
            )
        )
        sys.exit(ERROR_CONFIG_FILE_ALREADY_EXISTS)

    # Create the config file.
    with open(config_path, 'w') as config_file:
        config_file.write(json.dumps(DEFAULT_CONFIG, indent=4))
    print(
        'Configuration created in `{}`. Please edit to suit your '
        'own setup.'.format(
            config_path
        )
    )
    sys.exit(0)

def start_cursebox(
    window,
    server_name,
    server_port,
    username,
    password,
    player_id
):
    """A small helper function to get started."""
    cb = Cursebox(window)
    if server_port is None:
        server_port = DEFAULT_CONFIG.get('server').get('port')
    cb.start(server_name, server_port, username, password, player_id)

def main():
    """The main application."""
    # Read command line arguments.
    argv = sys.argv[1:]

    # Parse options.
    try:
        opts, args = getopt.getopt(argv, 'c:s:p:u:P:b:h', [
            'config=',
            'server=',
            'port=',
            'username=',
            'password=',
            'player_id=',
            'help',
        ])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # Handle options.
    config_path = None
    server_name = None
    server_port = None
    player_id = None
    username = None
    password = None

    # Extract options.
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-c', '--config'):
            config_path = arg
        elif opt in ('-s', '--server'):
            server_name = arg
        elif opt in ('-p', '--port'):
            server_port = arg
        elif opt in ('-b', '--player_id'):
            player_id = arg
        elif opt in ('-u', '--username'):
            username = arg
        elif opt in ('-P', '--password'):
            password = arg

    # Make sure at most a single argument is provided.
    if len(args) > 1:
        print('Only a single argument is allowed. You provided {}.'.format(
            len(args)
        ))
        sys.exit(ERROR_TOO_MANY_ARGUMENTS)

    # Act upon argument, if provided.
    if args:
        if args[0] != 'create-config':
            print('Unknown argument "{}".'.format(args[0]))
            sys.exit(ERROR_UNKNOWN_ARGUMENT)
        else:
            create_default_config(DEFAULT_CONFIG_PATH)
            sys.exit(0)

    # Read config file, if set and/or present.

    # Fall back to default config path, if file exists.
    if not config_path:
        default_config_path = DEFAULT_CONFIG_PATH
        if '~' in default_config_path:
            default_config_path = os.path.expanduser(default_config_path)
        if os.path.exists(default_config_path):
            config_path = default_config_path

    # Try to load config, if set.
    if config_path:
        # Check that config file exists.
        if '~' in config_path:
            config_path = os.path.expanduser(config_path)
        if not os.path.exists(config_path):
            print('Configuration file `{}` not found.'.format(
                config_path
            ))
            sys.exit(ERROR_CONFIG_FILE_NOT_FOUND)
        # Read config file.
        with open(config_path, 'r') as config_file:
            config = json.loads(config_file.read())
        # Parse config options, but don't override if already specified by
        # as options.
        if 'server' in config.keys():
            server_config = config.get('server')
            if not server_name:
                server_name = server_config.get('host', None)
            if not server_port:
                server_port = server_config.get('port', None)
                if not server_port:
                    server_port = 9090
            if not username:
                username = server_config.get('username', None)
            if not password:
                password = server_config.get('password', None)
        if 'selected_player' in config.keys():
            player_config = config.get('selected_player')
            if not player_id:
                player_id = player_config.get('id', None)

    # Make sure mandatory options are set.
    if server_name is None:
        usage()
        sys.exit(ERROR_MANDATORY_OPTIONS_MISSING)


    # Run cursebox.
    curses.wrapper(
        start_cursebox,
        server_name,
        server_port,
        username,
        password,
        player_id
    )

if __name__ == '__main__':
    main()
