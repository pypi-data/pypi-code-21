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
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Gio
import urllib.parse
import os.path

import ampd

from gampc import data
from gampc import module
from gampc import plugin
from gampc.utils import action
from gampc.utils import omenu
from gampc.utils import config


class SongList(module.Module):
    sortable = False
    duplicate_test_columns = []
    duplicate_field = '_duplicate'
    use_provided = ['songlist']

    CAPABILITIES_DRAG_DEST = 1
    CAPABILITIES_DRAG_SOURCE = 2

    capabilities = 0

    def __init__(self, shared):
        super().__init__(shared)
        self.fields = self.shared.songlist_fields

        self.treeview = data.RecordTreeView(self.fields, self.data_func, self.sortable)

        self.store = self.treeview.get_model()

        self.actions.add_action(action.Action('reset', self.action_reset_cb))
        self.actions.add_action(action.Action('copy', self.action_copy_delete_cb))

        dndtargets = [Gtk.TargetEntry.new('GAMPC_SONGS', Gtk.TargetFlags(0), 0)]

        if self.new_song != NotImplemented:
            self.actions.add_action(action.Action('paste', self.action_paste_cb))
            self.actions.add_action(action.Action('paste-before', self.action_paste_cb))
            self.treeview.drag_dest_set(Gtk.DestDefaults.DROP, dndtargets, Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
            self.signal_handler_connect(self.store, 'record-new', self.new_song)

        if self.delete_song != NotImplemented:
            self.actions.add_action(action.Action('delete', self.action_copy_delete_cb))
            self.actions.add_action(action.Action('cut', self.action_copy_delete_cb))
            self.treeview.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, dndtargets, Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
            self.signal_handler_connect(self.store, 'record-delete', self.delete_song)
        else:
            self.treeview.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, dndtargets, Gdk.DragAction.COPY)

        self.treeview_filter = data.TreeViewFilter(shared, self.treeview)
        self.add(self.treeview_filter)
        self.actions.add_action(action.PropertyAction('filter', self.treeview_filter, 'active'))

        self.setup_context_menu(self.provided.get('context_menu_items', []), self.treeview)
        self.treeview.connect('row-activated', self.treeview_row_activated_cb)

        self.connect('map', self.set_color)
        self.signal_handler_connect(self.shared, 'notify::dark', self.set_color)

    def set_color(self, *args):
        if self.win:
            self.color = self.win.get_style_context().get_color(Gtk.StateFlags.NORMAL)

    def action_copy_delete_cb(self, action, parameter):
        songs, refs = self.treeview.get_selection_rows()
        if action.get_name() in ['copy', 'cut']:
            Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(repr(songs), -1)
        if action.get_name() in ['delete', 'cut']:
            self.store.delete_refs(refs)

    def action_paste_cb(self, action, parameter):
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).request_text(self.treeview.clipboard_paste_cb, action.get_name().endswith('before'))

    @ampd.task
    async def treeview_row_activated_cb(self, treeview, p, column):
        if self.shared.restricted:
            return
        filename = self.store.get_record(self.store.get_iter(p)).file
        songs = await self.ampd.playlistfind('file', filename)
        if songs:
            song_id = sorted(songs, key=lambda song: song['Pos'])[0]['Id']
        else:
            song_id = await self.ampd.addid(filename)
        await self.ampd.playid(song_id)

    def get_filenames(self, selection=True):
        if selection:
            store, paths = self.treeview.get_selection().get_selected_rows()
            rows = (store.get_record(store.get_iter(p)) for p in paths)
        else:
            rows = (self.store.get_record(self.store.iter_nth_child(None, i)) for i in range(self.store.iter_n_children()))
        return (row.file for row in rows if row)

    def _mix_colors(self, r, g, b):
        return Gdk.RGBA((1 - self.color.red) * r + 0.5 * (1 - r),
                        (1 - self.color.green) * g + 0.5 * (1 - g),
                        (1 - self.color.blue) * b + 0.5 * (1 - b),
                        1.0)

    def _mix_colors_rgba(self, rgba):
        return self._mix_colors(rgba.red, rgba.green, rgba.blue)

    def data_func(self, column, renderer, store, i, j):
        _duplicate = store.get_record(i)._data.get(self.duplicate_field, None)
        if _duplicate is None:
            renderer.set_property('background-rgba', None)
        else:
            N = 4
            m = _duplicate % (N ** 3 - 1)
            renderer.set_property('background-rgba',
                                  self._mix_colors(*(float((m // (N ** k)) % N) / (N - 1)
                                                     for k in (2, 1, 0))))

    def set_songs(self, songs, set_fields=True):
        if set_fields:
            self.records_set_fields(songs)
        if self.duplicate_test_columns:
            self.find_duplicates(songs, self.duplicate_test_columns)
        self.store.set_rows(songs)

    def records_set_fields(self, songs):
        self.fields.records_set_fields(songs)

    def find_duplicates(self, songs, test_fields):
        dup_marker = 0
        dup_dict = {}
        for song in songs:
            if 'Time' not in song or int(song['Time']) <= 3:
                continue
            test = tuple(song.get(field) for field in test_fields)
            duplicates = dup_dict.get(test)
            if duplicates:
                if len(duplicates) == 1:
                    duplicates[0][self.duplicate_field] = dup_marker
                    dup_marker += 1
                song[self.duplicate_field] = duplicates[0][self.duplicate_field]
                duplicates.append(song)
            else:
                dup_dict[test] = [song]
                song.pop(self.duplicate_field, None)

    def action_reset_cb(self, action, parameter):
        self.treeview_filter.filter_.set_data({})
        self.treeview_filter.active = False
        if self.sortable:
            self.store.set_sort_column_id(-1, Gtk.SortType.ASCENDING)

    delete_song = new_song = NotImplemented


class SongListWithTotals(SongList):
    def set_songs(self, songs, set_fields=True):
        super().set_songs(songs, set_fields)
        time = sum(int(song.get('Time', '0')) for song in songs)
        self.status = '{} / {}'.format(len(songs), data.format_time(time))


class EditableSongListBase(SongList):
    SONG_NEW = 1
    SONG_DELETED = 2
    SONG_MODIFIED = 3
    SONG_UNDEFINED = 4

    STATUS_PROPERTIES = ('background-rgba', 'font', 'strikethrough')
    STATUS_PROPERTY_TABLE = {
        SONG_NEW: (Gdk.RGBA(0.0, 1.0, 0.0, 1.0), 'bold', None),
        SONG_DELETED: (Gdk.RGBA(1.0, 0.0, 0.0, 1.0), 'italic', True),
        SONG_MODIFIED: (Gdk.RGBA(1.0, 1.0, 0.0, 1.0), None, None),
        SONG_UNDEFINED: (None, 'bold italic', None),
    }

    def __init__(self, shared):
        super().__init__(shared)
        self.actions.add_action(action.Action('save', self.action_save_cb))
        self.actions.add_action(action.Action('undelete', self.action_undelete_cb))

    def data_func(self, column, renderer, store, i, j):
        for p in self.STATUS_PROPERTIES:
            renderer.set_property(p, None)
        super().data_func(column, renderer, store, i, j)
        status = store.get_record(i)._status
        if status is not None:
            for k, p in enumerate(self.STATUS_PROPERTIES):
                if self.STATUS_PROPERTY_TABLE[status][k] is not None:
                    renderer.set_property(p, self.STATUS_PROPERTY_TABLE[status][k])

    def action_undelete_cb(self, action, parameter):
        store, paths = self.treeview.get_selection().get_selected_rows()
        for p in paths:
            i = self.store.get_iter(p)
            if self.store.get_record(i)._status == self.SONG_DELETED:
                del self.store.get_record(i)._status
        self.treeview.queue_draw()

    def delete_song(self, store, i):
        if store.get_record(i)._status == self.SONG_UNDEFINED:
            return
        self.set_modified()
        if store.get_record(i)._status == self.SONG_NEW:
            store.remove(i)
        else:
            self.store.get_record(i)._status = self.SONG_DELETED
            self.merge_new_del(i)
        self.treeview.queue_draw()

    def merge_new_del(self, i):
        _status = self.store.get_record(i)._status
        for f in [self.store.iter_previous, self.store.iter_next]:
            j = f(i)
            if j and self.store.get_record(j).file == self.store.get_record(i).file and {_status, self.store.get_record(j)._status} == {self.SONG_DELETED, self.SONG_NEW}:
                del self.store.get_record(i)._status
                self.store.remove(j)
                return


class EditableSongList(EditableSongListBase):
    def new_song(self, store, i):
        self.set_modified()
        store.get_record(i)._status = self.SONG_NEW
        self.merge_new_del(i)


class EditableFileSongList(EditableSongListBase):
    def records_set_fields(self, songs):
        for song in songs:
            gfile = Gio.File.new_for_path(GLib.build_filenamev([self.shared.config.songlist.music_dir, song['file']]))
            if gfile.query_exists():
                song['_gfile'] = gfile
            else:
                song['_status'] = self.SONG_UNDEFINED
        super().records_set_fields(songs)

    def action_save_cb(self, action, parameter):
        self.save_files(song for i, p, song in self.store)

    def action_save_selected_cb(self, action, parameter):
        songs, refs = self.treeview.get_selection_rows()

    def save_files(self, songs):
        deleted = [song for song in songs if song._status == self.SONG_DELETED]
        if deleted:
            dialog = Gtk.Dialog(parent=self.win, title=_("Move to trash"))
            dialog.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
            dialog.add_button(_("_OK"), Gtk.ResponseType.OK)
            dialog.get_content_area().add(Gtk.Label(label='\n\t'.join([_("Move these files to the trash?")] + [song.file for song in deleted]), visible=True))
            reply = dialog.run()
            dialog.destroy()
            if reply != Gtk.ResponseType.OK:
                return
            for song in deleted:
                song._gfile.trash()
                song._status = self.SONG_UNDEFINED

    def set_modified(self):
        self.status = _("modified")

    def set_songs(self, songs, set_fields=True):
        self.status = None
        super().set_songs(songs, set_fields)


class SongListExtension(plugin.Extension):
    def __init__(self):
        super().__init__()
        self.provides['app'] = {}
        self.provides['app']['menubar_items'] = [
            omenu.Item('20#edit/10#global/10', 'mod.save', _("Save"), ['<Control>s']),
            omenu.Item('20#edit/10#global/20', 'mod.reset', _("Reset"), ['<Control>r']),
            omenu.Item('20#edit/10#global/30', 'mod.filter', _("Filter"), ['<Control><Shift>f']),
        ]
        self.provides['songlist'] = {}
        self.provides['songlist']['context_menu_items'] = []

        for items, prefix in ((self.provides['app']['menubar_items'], '20#edit/20#local/'),
                              (self.provides['songlist']['context_menu_items'], '50#edit/')):
            items += [
                omenu.Item(prefix + '10', 'mod.cut', _("Cut"), ['<Control>x'], accels_fragile=True),
                omenu.Item(prefix + '20', 'mod.copy', _("Copy"), ['<Control>c'], accels_fragile=True),
                omenu.Item(prefix + '30', 'mod.paste', _("Paste"), ['<Control>v'], accels_fragile=True),
                omenu.Item(prefix + '40', 'mod.paste-before', _("Paste before"), ['<Control>b']),
                omenu.Item(prefix + '50', 'mod.delete', _("Delete"), ['Delete'], accels_fragile=True),
                omenu.Item(prefix + '60', 'mod.undelete', _("Undelete"), ['<Alt>Delete'], accels_fragile=True),
            ]

    # try:
    #     import mutagen
    # except:
    #     mutagen = None

    @staticmethod
    def song_title(song):
        title = song.get('Title') or song.get('Name', '')
        filename = song.get('file', '')
        url = urllib.parse.urlparse(filename)
        if url.scheme:
            url_basename = os.path.basename(url.path)
            title = '{0} [{1}]'.format(title, url_basename) if title else url_basename
        return title

    def get_mutagen_file(self, song):
        return None
        if self.mutagen is None:
            return None
        try:
            return self.mutagen.File(song['_gfile'].get_path())
        except:
            return None

    @staticmethod
    def get_mutagen_bitrate(song):
        if '_mutagen' not in song:
            return None
        try:
            return str(song['_mutagen'].info.bitrate // 1000)
        except:
            if song['file'].endswith('.flac'):
                return 'FLAC'
            else:
                return '???'

    def activate(self):
        self.config = config.ConfigDict.load('songlist', self.shared.config)
        self.config.access('music-dir', GLib.get_user_special_dir(GLib.USER_DIRECTORY_MUSIC))

        self.shared.songlist_fields = data.FieldFamily(self.config.fields)
        self.shared.songlist_fields.register_field(data.Field('Album', _("Album")))
        self.shared.songlist_fields.register_field(data.Field('AlbumArtist', _("Album artist")))
        self.shared.songlist_fields.register_field(data.Field('Artist', _("Artist")))
        self.shared.songlist_fields.register_field(data.Field('Composer', _("Composer")))
        self.shared.songlist_fields.register_field(data.Field('Date', _("Date")))
        self.shared.songlist_fields.register_field(data.Field('Disc', _("Disc")))
        self.shared.songlist_fields.register_field(data.Field('file', _("File")))
        self.shared.songlist_fields.register_field(data.Field('Genre', _("Genre")))
        # self.shared.songlist_fields.register_field(data.Field('Last_Modified', _("Last modified"), get_value=lambda song: song.get('Last-Modified')))
        self.shared.songlist_fields.register_field(data.Field('Last_Modified', _("Last modified")))
        self.shared.songlist_fields.register_field(data.Field('Performer', _("Performer")))
        self.shared.songlist_fields.register_field(data.Field('Time', _("Seconds"), visible=False))
        self.shared.songlist_fields.register_field(data.Field('FormattedTime', _("Duration"), get_value=lambda song: data.format_time(song['Time']) if 'Time' in song else ''))
        self.shared.songlist_fields.register_field(data.Field('Title', _("Title (partial)")))
        self.shared.songlist_fields.register_field(data.Field('FullTitle', _("Title"), get_value=self.song_title))
        self.shared.songlist_fields.register_field(data.Field('Track', _("Track")))
        self.shared.songlist_fields.register_field(data.FieldWithTable(
            'Extension', _("Extension"),
            table=[
                [
                    'file',
                    '^http://',
                    ''
                ],
                [
                    'file',
                    '\\.([^.]*)$',
                    '\\1'
                ]
            ]))
        self.shared.songlist_fields.register_field(data.FieldWithTable(
            'agenre', visible=False,
            table=[
                [
                    'Genre',
                    '[Mm]ilong',
                    'b milonga'
                ],
                [
                    'Genre',
                    '[Cc]andombe',
                    'b milonga'
                ],
                [
                    'Genre',
                    '[Tt]ango|Canci[oó]n',
                    'a tango'
                ],
                [
                    'Genre',
                    '[Vv]als',
                    'c vals'
                ],
                [
                    'Genre',
                    '[Ff]ox ?trot',
                    'd fox'
                ],
                [
                    'Genre',
                    '[Pp]aso ?doble',
                    'e paso'
                ],
                [
                    'Genre',
                    'Ranchera',
                    'f ranchera'
                ],
                [
                    None,
                    None,
                    'z'
                ]
            ]))
        self.shared.songlist_fields.register_field(data.FieldWithTable(
            'ArtistSortName', visible=False,
            table=[
                [
                    'Artist',
                    '(La Típica Sanata|Otros Aires|.* Orquesta)',
                    '\\1'
                ],
                [
                    'Artist',
                    '^(.* Tango)$',
                    '\\1'
                ],
                [
                    'Artist',
                    '(.*), dir\. (.*) ([^ ]+)',
                    '\\3, \\2 (\\1)'
                ],
                [
                    'Artist',
                    '(Orquesta Típica|Dúo|Cuarteto|Sexteto) (.*)',
                    '\\2, \\1'
                ],
                [
                    'Artist',
                    '(.*) ((?:Di|De) *[^ ]+)',
                    '\\2, \\1'
                ],
                [
                    'Artist',
                    '(.*) ([^ ]+)',
                    '\\2, \\1'
                ],
                [
                    'Artist',
                    '(.*)',
                    '\\1'
                ]
            ]))
        performer_last_name = data.FieldWithTable(
            'PerformerLastName', visible=False,
            table=[
                [
                    'Performer',
                    '^(.*) ((?:Di|De|Del) *[^ ]+)$',
                    '\\2'
                ],
                [
                    'Performer',
                    '^(.*) ([^ ]+)$',
                    '\\2'
                ],
                [
                    'Performer',
                    '^(.*)$',
                    '\\1'
                ]
            ])
        self.shared.songlist_fields.register_field(data.Field(
            'PerformersLastNames', visible=False,
            get_value=lambda song: ', '.join(performer_last_name.get_value({'Performer': name}) for name in song.get('Performer').split(', ')) if song.get('Performer') else None))

    def deactivate(self):
        del self.shared.songlist_fields
