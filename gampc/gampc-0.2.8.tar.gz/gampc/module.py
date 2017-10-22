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


from gi.repository import GObject, Gio, Gtk, Gdk
import types
import asyncio

from . import data
from .utils import omenu
from .utils import config
from .utils.logger import logger


class Module(Gtk.Bin):
    title = None
    name = None
    key = None
    action_prefix = 'mod'
    use_provided = []
    replace = None

    status = GObject.property()
    full_title = GObject.property(type=str)

    def __init__(self, shared):
        super(Module, self).__init__(visible=True, full_title=self.title)
        self.signal_handlers = []

        self.bind_property('status', self, 'full-title', GObject.BindingFlags(0), lambda x, y: "{} [{}]".format(self.title, self.status) if self.status else self.title)

        self.connect('destroy', self.__destroy_cb)
        self.connect('map', self.__map_cb)
        self.connect('unmap', self.__unmap_cb)
        self.shared = shared
        self.config = config.ConfigDict.load(self.name, shared.config)
        self.ampd = self.shared.ampd_client.executor.sub_executor()
        self.signal_handler_connect(self.shared.ampd_client, 'client-connected', self.client_connected_cb)
        if self.shared.ampd_client.is_connected:
            self.client_connected_cb(self.shared.ampd_client)
        self.actions = Gio.SimpleActionGroup()
        self.signals = {}
        self.win = None
        self.provided = shared.collect_plugin_provides([self.name] + self.use_provided)
        for model in self.provided.get('actions', []):
            self.actions.add_action(model.create_action(lambda f: types.MethodType(f, self)))

    def __del__(self):
        logger.debug('Deleting {}'.format(self))

    @staticmethod
    def __destroy_cb(self):
        for target, handler in self.signal_handlers:
            target.disconnect(handler)
        del self.signal_handlers
        asyncio.ensure_future(self.ampd.close())
        del self.signals
        del self.actions

    def signal_handler_connect(self, target, *args):
        handler = target.connect(*args)
        self.signal_handlers.append((target, handler))

    def setup_context_menu(self, items, widget):
        if not items:
            return
        context_menu = omenu.OrderedMenu()
        for item in items:
            context_menu.insert(item)
        gtk_context_menu = Gtk.Menu.new_from_model(context_menu)
        gtk_context_menu.insert_action_group(self.action_prefix, self.actions)
        widget.connect('button-press-event', self.context_menu_button_press_event_cb, gtk_context_menu)

    @staticmethod
    def context_menu_button_press_event_cb(widget, event, context_menu):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            context_menu.popup(None, None, None, None, event.button, event.time)
            return True
        return False

    @staticmethod
    def client_connected_cb(client):
        pass

    @staticmethod
    def __map_cb(self):
        self.win = self.get_toplevel()
        self.win.insert_action_group(self.action_prefix, self.actions)
        for name, cb in self.signals.items():
            self.win.connect(name, cb)
        self.connect('notify::title-extra', self.win.update_title)

    @staticmethod
    def __unmap_cb(self):
        self.disconnect_by_func(self.win.update_title)
        if self.win.get_action_group(self.action_prefix) == self.actions:
            self.win.insert_action_group(self.action_prefix, None)
        for cb in self.signals.values():
            self.win.disconnect_by_func(cb)
        self.win = None


class PanedModule(Module):
    PANE_SEPARATOR_CONFIG = 'pane_separator'
    PANE_SEPARATOR_DEFAULT = 100

    def __init__(self, shared):
        super(PanedModule, self).__init__(shared)

        self.left_treeview = Gtk.TreeView(visible=True)
        self.scrolled_left_treeview = Gtk.ScrolledWindow(visible=True)
        self.scrolled_left_treeview.add(self.left_treeview)
        self.left_treeview.get_selection().connect('changed', self.left_treeview_selection_changed_cb)
        self.left_treeview.set_search_equal_func(lambda store, col, key, i: key.lower() not in store.get_value(i, col).lower())

        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL, position=self.config.access(self.PANE_SEPARATOR_CONFIG, self.PANE_SEPARATOR_DEFAULT), visible=True)
        self.paned.connect('notify::position', self.paned_notify_position_cb)
        self.paned.add1(self.scrolled_left_treeview)
        super(PanedModule, self).add(self.paned)

        self.setup_context_menu(self.provided.get('left_context_menu_items', []), self.left_treeview)

        self.starting = True
        self.connect('map', self.__map_cb)

    @staticmethod
    def __map_cb(self):
        if self.starting:
            self.left_treeview.grab_focus()
            self.starting = False

    def paned_notify_position_cb(self, *args):
        self.config[self.PANE_SEPARATOR_CONFIG] = self.paned.get_position()

    def left_store_set_rows(self, rows):
        data.store_set_rows(self.left_store, rows, lambda i, name: self.left_store.set_value(i, 0, name))

    def add(self, child):
        self.paned.add2(child)

    def remove(self, child):
        self.paned.remove2(child)
