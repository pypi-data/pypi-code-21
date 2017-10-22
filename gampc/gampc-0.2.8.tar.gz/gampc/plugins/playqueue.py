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


from gi.repository import GLib
from gi.repository import Gtk

import ampd

from gampc import plugin
from gampc.utils import action
from gampc.utils import omenu
from gampc.utils import ssde

import songlist


class PlayQueue(songlist.SongListWithTotals):
    title = _("Play Queue")
    name = 'playqueue'
    key = '1'

    duplicate_test_columns = ['Title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions.add_action(action.Action('playqueue-shuffle', self.action_shuffle_cb, restrict=True, shared=self.shared))
        self.actions.add_action(action.Action('playqueue-add-url', self.action_add_url_cb))
        self.actions.add_action(action.Action('playqueue-go-to-current', self.action_go_to_current_cb))
        self.signal_handler_connect(self.shared.ampd_server_properties, 'notify::current-song', self.notify_current_song_cb)
        for name in self.actions.list_actions():
            if name.startswith('playqueue-ext-'):
                self.actions.remove(name)

    @ampd.task
    async def client_connected_cb(self, client):
        while True:
            self.set_songs(await self.ampd.playlistinfo())
            await self.ampd.idle(ampd.PLAYLIST)

    def data_func(self, column, renderer, store, i, j):
        super().data_func(column, renderer, store, i, j)
        if self.shared.ampd_server_properties.state != 'stop' and store.get_record(i).Id == self.shared.ampd_server_properties.current_song.get('Id'):
            renderer.set_property('font', 'italic bold')
            bg = self._mix_colors(1, 1, 1)

            renderer.set_property('background-rgba', bg)
        else:
            renderer.set_property('font', None)

    @ampd.task
    async def action_shuffle_cb(self, action, parameter):
        await self.ampd.shuffle()

    def action_go_to_current_cb(self, action, parameter):
        if self.shared.ampd_server_properties.current_song:
            p = Gtk.TreePath.new_from_string(self.shared.ampd_server_properties.current_song['Pos'])
            self.treeview.set_cursor(p)
            self.treeview.scroll_to_cell(p, None, True, 0.5, 0.0)

    def notify_current_song_cb(self, *args):
        self.treeview.queue_draw()

    def new_song(self, store, i):
        ampd.Task(self.ampd.addid(store.get_record(i).file, store.get_path(i).get_indices()[0]))

    def delete_song(self, store, i):
        song_id = store.get_record(i).Id
        m = int(store.get_string_from_iter(i))
        for n in range(store.iter_n_children()):
            if n != m and store.get_record(store.iter_nth_child(None, n)).Id == song_id:
                ampd.Task(self.ampd.command_list((self.ampd.swap(n, m), self.ampd.delete(m))))
                store.remove(i)
                return
        if not (self.shared.restricted and self.shared.ampd_server_properties.state == 'play' and self.shared.ampd_server_properties.current_song.get('pos') == song_id):
            ampd.Task(self.ampd.deleteid(song_id))
            store.remove(i)

    @ampd.task
    async def treeview_row_activated_cb(self, treeview, p, column):
        if not self.shared.restricted:
            await self.ampd.playid(self.store.get_record(self.store.get_iter(p)).Id)

    @ampd.task
    async def action_add_url_cb(self, action, parameter):
        await self.ampd.ping()
        struct = ssde.Text(label=_("URL to add"), default='http://')
        url = struct.edit(self.win)
        if url:
            await self.ampd.add(url)


@ampd.task
async def action_playqueue_add_replace_cb(songlist_, action, parameter):
    filenames = songlist_.get_filenames(parameter.get_boolean())
    replace = '-replace' in action.get_name()
    shuffle = '-shuffle' in action.get_name()
    if replace:
        await songlist_.ampd.clear()
    await songlist_.ampd.command_list(songlist_.ampd.add(filename) for filename in filenames)
    if shuffle:
        await songlist_.ampd.shuffle()
    if replace:
        await songlist_.ampd.play()


class PlayQueueExtension(plugin.Extension):
    modules = [PlayQueue]

    def activate(self):
        self.provides['app'] = {}
        self.provides['app']['menubar_items'] = [
            omenu.Item('20#edit/90#playqueue/20', 'mod.playqueue-shuffle', _("Shuffle")),
            omenu.Item('20#edit/90#playqueue/30', 'mod.playqueue-add-url', _("Add URL")),
            omenu.Item('20#edit/90#playqueue/40', 'mod.playqueue-go-to-current', _("Go to current song"), ['<Control>z'])
        ]

        self.provides['songlist'] = {}
        self.provides['songlist']['actions'] = [
            action.ActionModel('playqueue-ext' + verb + shuffle, action_playqueue_add_replace_cb,
                               restrict=(verb == '-replace' or shuffle), parameter_type=GLib.VariantType.new('b'), shared=self.shared)
            for verb in ('-add', '-replace') for shuffle in ('', '-shuffle')
        ]
        for name, parameter in (('context_menu_items', '(true)'), ('left_context_menu_items', '(false)')):
            self.provides['songlist'][name] = [
                omenu.Item('10/1', 'mod.playqueue-ext-add' + parameter, _("Add to play queue")),
                omenu.Item('10/2', 'mod.playqueue-ext-replace' + parameter, _("Replace play queue")),
                omenu.Item('15/1', 'mod.playqueue-ext-add-shuffle' + parameter, _("Add to play queue & shuffle")),
                omenu.Item('15/2', 'mod.playqueue-ext-replace-shuffle' + parameter, _("Replace play queue & shuffle")),
            ]

        self.provides[PlayQueue.name] = {}
        self.provides[PlayQueue.name]['context_menu_items'] = [
            omenu.Item('90/10', 'mod.playqueue-shuffle', _("Shuffle")),
            omenu.Item('90/20', 'mod.playqueue-add-url', _("Add URL")),
        ]
