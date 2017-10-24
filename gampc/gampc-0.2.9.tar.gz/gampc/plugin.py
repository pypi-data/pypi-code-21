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


from gi.repository import GObject, Gtk, Gdk, Peas

from . import setup_locale


class Extension(GObject.Object, Peas.Activatable):
    object = GObject.Property(type=GObject.Object)
    modules = []
    setup_locale()

    def __init__(self):
        super().__init__()
        self.provides = {}

    @staticmethod
    def activate():
        pass

    @staticmethod
    def deactivate():
        pass


class ExtensionWithCss(Extension):
    def __init__(self):
        super(ExtensionWithCss, self).__init__()
        self.css_provider = Gtk.CssProvider.new()
        self.css_provider.load_from_data(self.css)

    def activate(self):
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def deactivate(self):
        Gtk.StyleContext.remove_provider_for_screen(Gdk.Screen.get_default(), self.css_provider)
