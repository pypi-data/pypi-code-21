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


from gi.repository import Gio, GLib


class Item(object):
    def __init__(self, path, target, label=None, accels=None, **attributes):
        """
        path = NAME/NAME/..../NAME
        target = Gio.MENU_LINK_SUBMENU | Gio.MENU_LINK_SECTION | detailed-action
        """

        self.path = path
        self.target = target
        self.label = label
        self.attributes = attributes
        self.attributes.setdefault('hidden-when', 'action-missing')
        if accels:
            self.attributes['accels'] = accels
            self.attributes['detailed-action'] = target

    def __repr__(self):
        return "{}({})".format(self.path, self.target)


class OrderedMenu(Gio.Menu):
    ATTRIBUTE_NAME = 'omenu-name'

    def __init__(self, _set_accels=None):
        super(OrderedMenu, self).__init__()
        self._set_accels = _set_accels

    def insert_path(self, path, target, label=None, accels=None, **attributes):
        return self.insert(Item(path, target, label, accels, **attributes))

    def insert(self, item):
        menu, i, found, name = self._find_path(item.path.split('/'))
        if found:
            if item.target in (Gio.MENU_LINK_SUBMENU, Gio.MENU_LINK_SECTION):
                submenu = menu.get_item_link(i, item.target)
                if submenu:
                    return submenu
            raise ValueError("Item already exists for path '{path}'".format(path=item.path))
        if self._set_accels and 'detailed-action' in item.attributes:
            self._set_accels(item.attributes['detailed-action'], item.attributes.get('accels', []))
        return menu._create_item(i, name, item.target, item.label, item.attributes)

    def remove_path(self, path):
        menu, i, found, name = self._find_path(path.split('/'))
        if found:
            action = menu.get_item_attribute_value(i, 'detailed-action')
            if action and self._set_accels:
                self._set_accels(action.unpack(), [])
            menu.remove(i)
        else:
            raise ValueError("Cannot remove inexistent path '{path}'".format(path=path))

    def enable_fragile_accels(self):
        for action, accels, fragile in self._action_accels():
            if fragile:
                self._set_accels(action, accels)

    def disable_fragile_accels(self):
        for action, accels, fragile in self._action_accels():
            if fragile:
                self._set_accels(action, [])

    def _create_item(self, i, name, target, label=None, attributes=None):
        item = Gio.MenuItem.new(label)
        item.set_attribute_value(self.ATTRIBUTE_NAME, GLib.Variant.new_string(name))
        if target in (Gio.MENU_LINK_SUBMENU, Gio.MENU_LINK_SECTION):
            submenu = OrderedMenu()
            item.set_link(target, submenu)
        else:
            submenu = None
            item.set_detailed_action(target)
            if attributes:
                for attribute, value in attributes.items():
                    if value is None:
                        continue
                    elif isinstance(value, str):
                        value = GLib.Variant.new_string(value)
                    elif isinstance(value, bool):
                        value = GLib.Variant.new_boolean(value)
                    else:
                        value = GLib.Variant.new_strv(value)
                    item.set_attribute_value(attribute.replace('_', '-'), value)
        self.insert_item(i, item)
        return submenu

    def _find_position(self, name):
        n = self.get_n_items()
        for i in range(n):
            item_name = self.get_item_attribute_value(i, self.ATTRIBUTE_NAME)
            item_name = item_name and item_name.get_string()
            if item_name is None or item_name >= name:
                return i, item_name == name
        return n, False

    def _find_path(self, names):
        menu = self
        last_name = names[0]
        i, found = self._find_position(last_name)
        for name in names[1:]:
            if not found:
                menu = menu._create_item(i, last_name, Gio.MENU_LINK_SECTION)
            else:
                menu = menu.get_item_link(i, Gio.MENU_LINK_SUBMENU) or menu.get_item_link(i, Gio.MENU_LINK_SECTION)
                if not menu:
                    raise ValueError("Path element '{name}' is not a submenu or section".format(name=last_name))
            i, found = menu._find_position(name)
            last_name = name

        return menu, i, found, last_name

    def _action_accels(self):
        for i in range(self.get_n_items()):
            submenu = self.get_item_link(i, Gio.MENU_LINK_SUBMENU) or self.get_item_link(i, Gio.MENU_LINK_SECTION)
            if submenu:
                yield from submenu._action_accels()
            else:
                item_accels = self.get_item_attribute_value(i, 'accels')
                item_accels_fragile = self.get_item_attribute_value(i, 'accels-fragile')
                if item_accels:
                    yield self.get_item_attribute_value(i, 'detailed-action').unpack(), item_accels.unpack(), item_accels_fragile and item_accels_fragile.unpack()
