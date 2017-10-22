# coding: utf-8
#
# Graphical Asynchronous Music Player Client
#
# Copyright (C) 2015 Itaï BEN YAACOV
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from gampc import plugin


def notify_current_song_cb(server_properties, param):
    server_properties.handler_block_by_func(notify_current_song_cb)
    if server_properties.current_song.get('Name') == 'RadioTango-Velours':
        try:
            artist, title = server_properties.current_song.get('Title').split(' - ')
            server_properties.current_song.setdefault('orig', server_properties.current_song.copy())
            server_properties.current_song.update(Artist=artist, Title=title, performer='Radio Tango Velours')
            server_properties.notify('current-song')
        except:
            pass
    server_properties.handler_unblock_by_func(notify_current_song_cb)


class TangoVeloursExtension(plugin.Extension):
    def activate(self):
        self.shared.ampd_server_properties.connect('notify::current-song', notify_current_song_cb)
        notify_current_song_cb(self.shared.ampd_server_properties, None)

    def deactivate(self):
        self.shared.ampd_server_properties.disconnect_by_func(notify_current_song_cb)
        orig = self.shared.ampd_server_properties.current_song.get('orig')
        if orig:
            self.shared.ampd_server_properties.current_song = orig
