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


from gi.repository import GObject, Gtk
import logging

from gampc import module
from gampc import plugin


class Handler(logging.Handler, GObject.GObject):
    log = GObject.property()

    def __init__(self):
        logging.Handler.__init__(self)
        GObject.GObject.__init__(self)
        self.flush()

    def emit(self, record):
        self.log.append(record)
        self.notify('log')

    def flush(self):
        self.log = []


class Log(module.Module):
    title = _("View log")
    name = 'log'
    key = '8'

    def __init__(self, *args):
        super(Log, self).__init__(*args)
        self.label = Gtk.Label(selectable=True, visible=True)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, visible=True)
        hbox.pack_start(self.label, False, False, 0)
        hbox.pack_end(Gtk.Label(), True, False, 0)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, visible=True)
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_end(Gtk.Label(), True, False, 0)
        self.scrolled_label = Gtk.ScrolledWindow(visible=True)
        self.scrolled_label.add(vbox)
        widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, visible=True)
        widget.pack_start(self.scrolled_label, True, True, 0)
        self.add(widget)

        handler = self.shared.log_handler
        self.signal_handler_connect(handler, 'notify::log', self.handler_notify_log_cb)
        self.scrolled_label.get_vadjustment().connect('changed', self.adjustment_changed_cb)
        self.handler_notify_log_cb(handler, None)

    def handler_notify_log_cb(self, handler, param):
        self.label.set_text('\n'.join(handler.format(record) for record in handler.log))

    def adjustment_changed_cb(self, adjustment):
        adjustment.set_value(adjustment.get_upper())


class LogExtension(plugin.Extension):
    modules = [Log]

    def activate(self):
        self.shared.log_handler = Handler()
        self.shared.log_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s: %(name)s: %(message)s (%(pathname)s %(lineno)d)'))
        logging.getLogger().addHandler(self.shared.log_handler)

    def deactivate(self):
        logging.getLogger().removeHandler(self.shared.log_handler)
        del self.shared.log_handler
