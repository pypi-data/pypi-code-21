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


from gi.repository import GObject, GLib, Gtk, Gdk
import logging

from .data import format_time
from .utils import action
from .utils.logger import logger


class WindowLoggingHandeler(logging.Handler):
    MAX_INFOBARS = 5

    def __init__(self, box, timeout):
        super(WindowLoggingHandeler, self).__init__(logging.INFO)
        self.box = box
        self.timeout = timeout

    def emit(self, record):
        children = self.box.get_children()
        nchildren = len(children)
        if nchildren >= self.MAX_INFOBARS:
            for child in children[:nchildren - self.MAX_INFOBARS + 1]:
                self.remove_infobar(child)
        message_type = Gtk.MessageType.ERROR if record.levelno >= 40 else Gtk.MessageType.WARNING if record.levelno >= 30 else Gtk.MessageType.INFO
        infobar = Gtk.InfoBar(visible=True, message_type=message_type)
        infobar.get_content_area().add(Gtk.Label(visible=True, label=record.msg))
        infobar.connect('response', self.remove_infobar)
        css_provider = Gtk.CssProvider.new()
        css_provider.load_from_data(b'infobar.error { background-image: linear-gradient(to top left, rgb(211,10,10), rgb(255,0,0)); }')
        infobar.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.box.add(infobar)
        infobar.timeout = GLib.timeout_add(self.timeout, self.remove_infobar, infobar)

    def remove_infobar(self, infobar, *args):
        GLib.source_remove(infobar.timeout)
        self.box.remove(infobar)

    def close(self):
        super(WindowLoggingHandeler, self).close()
        self.box.foreach(self.remove_infobar)


class Window(Gtk.ApplicationWindow):
    DEFAULT_TITLE = 'GAMPC'

    def __init__(self, app):
        super(Window, self).__init__(application=app)
        self.shared = app.shared
        self.is_fullscreen = False
        self.module = None

        self.config = self.shared.config.window
        self.config.access('message-timeout', 5)
        self.set_default_size(self.config.access('width', 1000),
                              self.config.access('height', 600))

        self.connect('destroy', self.destroy_cb)

        self.shared.ampd_server_properties.connect('notify::current-song', self.notify_current_song_cb)
        self.shared.ampd_server_properties.connect('notify::state', self.update_title)
        self.shared.connect('notify::server-label', self.update_subtitle)

        builder = self.shared.build_ui('window')

        self.option_buttons = {}
        for option in self.shared.ampd_server_properties.OPTION_NAMES:
            button = builder.get_object('togglebutton-' + option)
            self.shared.ampd_server_properties.bind_property('option-' + option, button, 'active', GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
            self.shared.bind_property('restricted', button, 'sensitive', GObject.BindingFlags.SYNC_CREATE, lambda binding, value: not value)
            self.option_buttons[option] = button
            self.option_notify_active_cb(button, None)
            button.connect('notify::active', self.option_notify_active_cb)

        self.scale_time = builder.get_object('scale-time')
        label_time = builder.get_object('label-time')
        label_time_total = builder.get_object('label-time-total')
        self.volume_button = builder.get_object('volume-button')

        self.main = builder.get_object('main')
        self.add(self.main)
        self.titlebar = builder.get_object('header')
        self.set_titlebar(self.titlebar)

        self.shared.ampd_server_properties.bind_property('state', builder.get_object('button-play'), 'visible', GObject.BindingFlags.SYNC_CREATE, lambda binding, value: value != 'play')
        self.shared.ampd_server_properties.bind_property('state', builder.get_object('button-pause'), 'visible', GObject.BindingFlags.SYNC_CREATE, lambda binding, value: value == 'play')
        self.shared.ampd_server_properties.bind_property('state', self.scale_time, 'sensitive', GObject.BindingFlags.SYNC_CREATE, lambda binding, value: value in {'play', 'pause'})
        self.shared.ampd_server_properties.bind_property('volume', self.volume_button, 'value', GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        self.shared.ampd_server_properties.bind_property('volume', self.volume_button, 'sensitive', GObject.BindingFlags.SYNC_CREATE, lambda binding, value: value != -1)
        self.shared.bind_property('restricted', builder.get_object('image-restricted'), 'visible', GObject.BindingFlags.SYNC_CREATE)
        self.shared.bind_property('restricted', self.scale_time, 'sensitive', GObject.BindingFlags.INVERT_BOOLEAN | GObject.BindingFlags.SYNC_CREATE)
        label_time.bind_property('visible', label_time_total, 'visible', GObject.BindingFlags.SYNC_CREATE)
        self.shared.ampd_server_properties.bind_property('bitrate', builder.get_object('label-bitrate'), 'label', GObject.BindingFlags.SYNC_CREATE, lambda binding, value: ' [{kbps}kbps]'.format(kbps=value) if value else '')
        self.shared.ampd_server_properties.bind_property('time', self.scale_time.get_adjustment(), 'upper', GObject.BindingFlags.SYNC_CREATE)
        self.shared.ampd_server_properties.bind_property('time', self.scale_time.get_adjustment(), 'value', GObject.BindingFlags.SYNC_CREATE, lambda binding, value: binding.get_source().elapsed)
        self.shared.ampd_server_properties.bind_property('elapsed', self.scale_time, 'fill-level', GObject.BindingFlags.SYNC_CREATE)
        self.scale_time_binding = None
        self.scale_time.get_adjustment().bind_property('value', label_time, 'label', GObject.BindingFlags.SYNC_CREATE, lambda binding, value: format_time(value + 0.5))
        self.scale_time.get_adjustment().bind_property('upper', label_time_total, 'label', GObject.BindingFlags.SYNC_CREATE, lambda binding, value: ' / ' + format_time(value))
        self.scale_time.get_adjustment().bind_property('upper', label_time, 'visible', GObject.BindingFlags.SYNC_CREATE, lambda binding, value: value != 0.0)
        self.set_scale_time_binding()

        self.add_action(action.Action('toggle-fullscreen', self.action_toggle_fullscreen_cb))
        self.add_action(action.Action('volume-popup', self.action_volume_popup_cb))

        builder.connect_signals(self)

        self.logging_handler = WindowLoggingHandeler(builder.get_object('box-info'), self.config.message_timeout * 1000)
        logger.addHandler(self.logging_handler)
        self.update_title()
        self.update_subtitle()

    @staticmethod
    def destroy_cb(self):
        logger.debug("Destroying window: {}".format(self))
        self.change_module(None)
        logger.removeHandler(self.logging_handler)
        self.logging_handler.close()
        self.shared.disconnect_by_func(self.update_subtitle)
        self.shared.ampd_server_properties.disconnect_by_func(self.update_title)
        self.shared.ampd_server_properties.disconnect_by_func(self.notify_current_song_cb)

    def option_notify_active_cb(self, button, param):
        option_name = '{name} mode'.format(name=button.get_name().capitalize())
        button.set_tooltip_text('{} {}'.format(_(option_name), _("on") if button.get_active() else _("off")))

    def change_module(self, module):
        if self.module:
            self.main.remove(self.module)
            self.module.disconnect_by_func(self.update_subtitle)
        self.module = module
        if module:
            self.main.pack_start(module, True, True, 0)
            self.module.connect('notify::full-title', self.update_subtitle)
        self.update_subtitle()

    def notify_current_song_cb(self, *args):
        self.scale_time_break_interaction()
        self.update_title()

    def update_title(self, *args):
        if self.shared.ampd_server_properties.state == 'stop':
            title = self.DEFAULT_TITLE
        else:
            title = '{} / {}'.format(self.shared.ampd_server_properties.current_song.get('Artist', ''), self.shared.ampd_server_properties.current_song.get('Title', ''))
            if self.shared.ampd_server_properties.state == 'pause':
                title += ' ({})'.format(_("paused"))
        self.titlebar.set_title(title)

    def update_subtitle(self, *args):
        components = []
        if self.module:
            components.append(self.module.full_title)
        if self.shared.server_label:
            components.append(self.shared.server_label)
        self.titlebar.set_subtitle(' / '.join(components))

    def do_check_resize(self):
        if not self.is_fullscreen:
            self.config.width, self.config.height = self.get_size()
        Gtk.ApplicationWindow.do_check_resize(self)

    def scale_time_button_press_event_cb(self, scale_time, event):
        if event.button == 1 and event.type == Gdk.EventType.BUTTON_PRESS and self.scale_time_binding:
            self.scale_time_binding.unbind()
            self.scale_time_binding = None
        else:
            self.scale_time_break_interaction()

    def scale_time_button_release_event_cb(self, scale_time, event):
        if not self.scale_time_binding:
            if event.button == 1 and event.state & (Gdk.ModifierType.SHIFT_MASK | Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK) == 0:
                self.shared.ampd_server_properties.elapsed = self.scale_time.get_value()
                self.set_scale_time_binding()
            else:
                self.scale_time_break_interaction()

    def scale_time_break_interaction(self, *args):
        if not self.scale_time_binding:
            self.scale_time.set_sensitive(False)
            GLib.timeout_add(0, self.scale_time.set_sensitive, True)

    def scale_time_notify_sensitive_cb(self, *args):
        if not self.scale_time.get_sensitive():
            self.set_scale_time_binding()

    def set_scale_time_binding(self):
        if not self.scale_time_binding:
            self.scale_time_binding = self.shared.ampd_server_properties.bind_property('elapsed', self.scale_time.get_adjustment(), 'value', GObject.BindingFlags.SYNC_CREATE)

    def action_toggle_fullscreen_cb(self, *args):
        if self.is_fullscreen:
            self.unfullscreen()
        else:
            self.fullscreen()

    def action_volume_popup_cb(self, action, parameter):
        if self.volume_button.is_sensitive() and not self.volume_button.get_popup().get_mapped():
            self.volume_button.emit('popup')
        else:
            self.volume_button.emit('popdown')

    def do_window_state_event(self, event):
        self.is_fullscreen = bool(event.new_window_state & Gdk.WindowState.FULLSCREEN)
        self.set_show_menubar(not self.is_fullscreen)
        self.titlebar.set_visible(not self.is_fullscreen)
        return Gtk.ApplicationWindow.do_window_state_event(self, event)
