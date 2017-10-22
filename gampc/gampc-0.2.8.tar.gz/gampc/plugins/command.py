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


from gi.repository import Gtk

import ampd

from gampc import module
from gampc import plugin


class Command(module.Module):
    title = _("Execute MPD commands")
    name = 'command'
    key = '7'

    def __init__(self, *args):
        super(Command, self).__init__(*args)
        self.label = Gtk.Label(max_width_chars=50, wrap=True, selectable=True, visible=True)
        self.entry = Gtk.Entry(visible=True)
        self.entry.connect('activate', self.entry_activate_cb)
        self.entry.connect('focus-in-event', self.entry_focus_cb)
        self.entry.connect('focus-out-event', self.entry_focus_cb)
        widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, visible=True)
        widget.pack_start(self.label, True, True, 0)
        widget.pack_end(self.entry, False, False, 0)
        self.add(widget)
        self.connect('map', lambda self: self.entry.grab_focus())

    @ampd.task
    async def entry_activate_cb(self, entry):
        reply = await self.ampd._raw(entry.get_text())
        self.label.set_label('\n'.join(str(x) for x in reply) if reply else _("Empty reply"))

    def entry_focus_cb(self, entry, event):
        self.shared.enable_fragile_accels = not event.in_
        return False


class CommandExtension(plugin.Extension):
    modules = [Command]
