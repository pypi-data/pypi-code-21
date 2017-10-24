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


from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Peas
import sys
import os
import xdg.BaseDirectory
import asyncio

import ampd

from .utils import db
from .utils import config
from .utils.logger import logger


class AppShared(GObject.GObject):
    want_to_connect = GObject.property(type=bool, default=False)
    restricted = GObject.property(type=bool, default=False)
    dark = GObject.property(type=bool, default=False)
    enable_fragile_accels = GObject.property(type=bool, default=True)
    server_label = GObject.property(type=str, default='')
    server_profile = GObject.property(type=str)

    CONFIG_EDIT_DIALOG_SIZE = 'edit-dialog-size'
    SEPARATOR_FILE = 'separator.mp3'
    STICKER_PROPERTIES = ('restricted', 'dark')

    def __init__(self):
        super(AppShared, self).__init__()
        self.uidefs = {}
        self.excepthook_orig, sys.excepthook = sys.excepthook, self.excepthook

        self.ampd_client = ampd.ClientGLib()
        self.ampd_client.connect('client-connected', self.client_connected_cb)
        self.ampd_client.connect('client-disconnected', self.client_disconnected_cb)
        self.ampd_server_properties = ampd.ServerPropertiesGLib(self.ampd_client)
        self.ampd_server_properties.connect('server-error', self.server_error_cb)
        for option in self.ampd_server_properties.OPTION_NAMES:
            self.ampd_server_properties.connect('notify::option-' + option, self.notify_option_cb)
        self.ampd_server_properties.connect('notify::updating-db', self.set_server_label)

        self.ampd_host = None
        self.ampd_port = 6600
        self.ampd = self.ampd_client.executor.sub_executor()

        self.peas_engine = Peas.Engine.get_default()
        self.peas_engine.enable_loader('python3')
        self.peas_extension_set = Peas.ExtensionSet.new(self.peas_engine, Peas.Activatable, [])
        self.peas_engine.add_search_path(os.path.join(os.path.dirname(__file__), 'plugins'))
        self.peas_engine.rescan_plugins()

        self.config = config.ConfigDict.load('config')

        self.config.server.access('profiles',
                                  [
                                      {
                                          'name': _("Local host"),
                                          'host': 'localhost',
                                          'port': 6600,
                                      },
                                  ])
        self.connect('notify::server-profile', self.ampd_connect)
        self.server_profile = self.config.server.access('profile', _("Local host"))

        self.separator_song = {'file': self.SEPARATOR_FILE}
        self.connect('notify', self.notify_sticker_cb)
        # self.restricted = self.config.access('restricted', False)
        self.connect('notify::restricted', self.notify_restricted_cb)
        self.connect('notify::dark', self.notify_dark_cb)

    def __del__(self):
        logger.debug('Deleting {}'.format(self))

    def close(self):
        logger.debug("Closing shared")
        self.config.save()
        asyncio.ensure_future(self.ampd_client.close())
        sys.excepthook = self.excepthook_orig
        self.disconnect_by_func(self.notify_restricted_cb)
        self.disconnect_by_func(self.notify_dark_cb)
        self.disconnect_by_func(self.notify_sticker_cb)
        self.disconnect_by_func(self.ampd_connect)
        self.ampd_server_properties.disconnect_by_func(self.set_server_label)
        del self.peas_extension_set
        del self.ampd_client
        del self.ampd_server_properties

    def build_ui(self, uiname):
        if uiname in self.uidefs:
            uidef = self.uidefs[uiname]
        else:
            uidef = open(os.path.join(os.path.dirname(__file__), uiname + '.ui')).read()
            self.uidefs[uiname] = uidef
        builder = Gtk.Builder(translation_domain='gampc')
        builder.add_from_string(uidef)
        return builder

    def client_connected_cb(self, client):
        logger.info(_("Connected to {profile} [protocol version {protocol}]").format(profile=self.config.server.profile, protocol=self.ampd.get_protocol_version()))
        self.idle_database()
        self.idle_sticker()

    @ampd.task
    async def client_disconnected_cb(self, client, reason, message):
        self.separator_song.clear()
        self.separator_song['file'] = self.SEPARATOR_FILE
        if reason == client.DISCONNECT_RECONNECT:
            return
        elif reason == client.DISCONNECT_PASSWORD:
            logger.error(_("Invalid password for {}").format(self.config.server.profile))
            return
        elif reason == client.DISCONNECT_FAILED_CONNECT:
            logger.error(_("Connection to {} failed").format(self.config.server.profile))
            if message:
                logger.error(message)
        else:
            logger.info(_("Disconnected from {}").format(self.config.server.profile))
        if self.want_to_connect:
            reply = await self.ampd.idle(ampd.CONNECT, timeout=1)
            if reply & ampd.TIMEOUT:
                asyncio.ensure_future(self.ampd_client.connect_to_server(self.ampd_host, self.ampd_port))

    def server_error_cb(self, client, error):
        logger.error(_("Server error: {error}").format(error=error))

    @ampd.task
    async def notify_option_cb(self, properties, param):
        if self.restricted:
            option = param.name.split('-')[1]
            await getattr(self.ampd, option)(0)

    @staticmethod
    def notify_restricted_cb(self, param):
        if self.restricted:
            for option in self.ampd_server_properties.OPTION_NAMES:
                self.ampd_server_properties.set_property('option-' + option, False)

    @staticmethod
    def notify_dark_cb(self, param):
        css = Gtk.CssProvider.get_named('Adwaita', 'dark' if self.dark else None)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    @staticmethod
    @ampd.task
    async def notify_sticker_cb(self, param):
        if param.name in self.STICKER_PROPERTIES:
            try:
                await self.ampd.sticker_set('song', self.SEPARATOR_FILE, param.name, str(self.get_property(param.name)))
            except ampd.errors.ReplyError:
                pass

    @ampd.task
    async def idle_database(self):
        while True:
            song = await self.ampd.find('file', self.SEPARATOR_FILE)
            if song:
                self.separator_song.update(song[0])
            else:
                GLib.timeout_add(0, self.separator_missing)
            await self.ampd.idle(ampd.DATABASE)
            logger.info(_("Database changed"))

    def separator_missing(self):
        dialog = Gtk.MessageDialog(message_type=Gtk.MessageType.WARNING,
                                   buttons=Gtk.ButtonsType.CLOSE,
                                   text=_("Some features require a file named '{separator}' at the music root directory.  Such a file, consisting of a three second silence, is provided.").format(separator=self.SEPARATOR_FILE))
        dialog.run()
        dialog.destroy()

    @ampd.task
    async def idle_sticker(self):
        while True:
            self.handler_block_by_func(self.notify_sticker_cb)
            try:
                properties = await self.ampd.sticker_list('song', self.SEPARATOR_FILE)
            except ampd.errors.ReplyError:
                properties = []
            for property_ in properties:
                key, value = property_.split('=', 1)
                if key in self.STICKER_PROPERTIES:
                    self.set_property(key, value == 'True')
            self.handler_unblock_by_func(self.notify_sticker_cb)
            await self.ampd.idle(ampd.STICKER)

    def ampd_connect(self, *args):
        self.want_to_connect = True
        self.config.server.profile = self.server_profile
        self.set_server_label()
        for profile in self.config.server.profiles:
            if profile['name'] == self.server_profile:
                self.ampd_host = profile['host']
                self.ampd_port = profile['port']
                asyncio.ensure_future(self.ampd_client.connect_to_server(self.ampd_host, self.ampd_port))
                return

    def ampd_disconnect(self, *args):
        self.want_to_connect = False
        asyncio.ensure_future(self.ampd_client.disconnect_from_server())
        self.set_server_label()

    def set_server_label(self, *args):
        if self.want_to_connect:
            self.server_label = self.config.server.profile
            if self.ampd_server_properties.updating_db:
                self.server_label += " [{}]".format(_("database update"))
        else:
            self.server_label = ''

    def excepthook(self, *args):
        if args[0] == ampd.errors.ReplyError:
            logger.error(args[1])
        else:
            logger.error(args[1], exc_info=args)
        try:
            del sys.last_type, sys.last_value, sys.last_traceback
        except:
            pass

    @staticmethod
    def sqlite_connection(name):
        connection = db.Connection(os.path.join(xdg.BaseDirectory.save_data_path('gampc'), name + '.sqlite'))
        connection.cursor().execute('PRAGMA FOREIGH_KEYS=ON')
        return connection

    def collect_plugin_provides(self, targets):
        provides = {}
        self.peas_extension_set.foreach(self.collect_plugin_provides_worker, targets, provides)
        return provides

    @staticmethod
    def collect_plugin_provides_worker(extension_set, info, extension, targets, provides):
        for target, target_provides in extension.provides.items():
            if target in targets:
                for key, value in target_provides.items():
                    key_provides = provides.setdefault(key, [])
                    key_provides += value
