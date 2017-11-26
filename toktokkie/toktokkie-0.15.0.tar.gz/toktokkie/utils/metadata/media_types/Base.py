"""
Copyright 2015-2017 Hermann Krumrey

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import json
from typing import Dict, List


class Base(object):
    """
    The base Media Type class.
    Implements common functions, JSON schema framework and automatic checks
    """

    identifier = "base"
    """
    An identifier string that indicates the type
    """

    # Getters
    @property
    def media_type(self) -> str:
        return self.info["type"]

    @property
    def name(self) -> str:
        return str(self.resolve_inner_attribute("name"))

    @property
    def tags(self) -> List[str]:
        # noinspection PyTypeChecker
        return self.resolve_inner_attribute("tags")

    @property
    def path(self) -> str:
        return os.path.join(self.root_path, self.child_key)

    # Setters
    @media_type.setter
    def media_type(self, value: str):
        self.info["type"] = value

    @name.setter
    def name(self, value: str):
        self.store_inner_attribute("name", value)

    @tags.setter
    def tags(self, value: List[str]):
        self.store_inner_attribute(
            "tags", list(map(lambda x: x.strip(), value))
        )

    def __init__(self, path: str, generate: bool = False,
                 overwrite_with_generated: bool = False):
        """
        Initializes a new Media Type object from a directory path
        :param path: The path for which to create the Media Type object
        :param generate: Can be set to True to generate the directory
                         and a basic info.json file.
        :param overwrite_with_generated: Can be set to True to overwrite any
                                         existing info.json file
                                         while generating.
        """
        self.extender_key = ""
        self.child_key = ""

        self.root_path = path
        self.info_file = os.path.join(path, ".meta", "info.json")

        if generate:
            metadir = os.path.join(path, ".meta")
            if not os.path.isdir(metadir):
                os.makedirs(metadir)
            if not os.path.isfile(self.info_file) or overwrite_with_generated:
                self.generate_info_file()

        with open(self.info_file, 'r') as info:
            self.info = json.loads(info.read())

        self.check_if_valid()

    def set_child_extender(self, extender_key: str, child_key: str):
        """
        Sets the extender_key and child_key attributes to handle this metadata
        object as if it were a child of it. Mostly affects getters and setters,
        as well as the saving procedure
        :param extender_key: The extender key. Example: 'seasons'
        :param child_key: The child key. Example: 'Season 2'
        :return: None
        """
        if extender_key not in self.define_attributes()["extenders"] \
                or child_key not in self.info[extender_key]:
            raise AttributeError("Invalid Extender/Child pair")
        else:
            self.extender_key = extender_key
            self.child_key = child_key

    def resolve_inner_attribute(self, attribute: str) -> object:
        """
        Resolves an attribute. Helper method for the getters and setters.
        The purpose of this method is to make handling children metadata
        objects easier
        :param attribute: The attribute to check for
        :return: the attribute value.
        """
        try:
            if self.extender_key\
                    and self.child_key\
                    and attribute \
                    in self.info[self.extender_key][self.child_key]:
                return self.info[self.extender_key][self.child_key][attribute]
            else:
                return self.info[attribute]

        except KeyError:
            return None

    def store_inner_attribute(self, attribute: str, value: object,
                              equality_check=lambda x, y: x == y):
        """
        Stores an attribute. Helper method for the setters that makes it easier
        to handle child metadata
        :param attribute: The attribute to set
        :param value: The value of the attribute to set
        :param equality_check: Lambda that checks for equality. Defaults to ==
        :return: None
        """
        if not self.extender_key or not self.child_key:
            if value is not None:
                self.info[attribute] = value
            elif attribute in self.info:
                self.info.pop(attribute)

        elif not equality_check(self.info[attribute], value):
            if value is not None:
                self.info[self.extender_key][self.child_key][attribute] = value
            elif attribute in self.info[self.extender_key][self.child_key]:
                self.info[self.extender_key][self.child_key].pop(attribute)

        # If the value is the same as the parents' we don't need to update
        else:
            # But we have to remove any existing values
            if attribute in self.info[self.extender_key][self.child_key]:
                self.info[self.extender_key][self.child_key].pop(attribute)

    def generate_info_file(self):
        """
        Generates a skeleton info.json file
        :return: None
        """
        data = {}
        attrs = self.define_attributes()
        for required in attrs["required"]:
            # noinspection PyCallingNonCallable
            data[required] = attrs["required"][required]()
        data["type"] = self.identifier
        data["name"] = os.path.basename(self.root_path)
        with open(self.info_file, 'w') as f:
            f.write(json.dumps(
                data,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            ))

    def check_if_valid(self):
        """
        Checks if the loaded JSON information is valid
        for the specified Media Type
        If not, raise a descriptive AttributeError
        """
        attrs = self.define_attributes()

        # Check if all required attributes exist and have the correct type
        for required in attrs["required"]:
            if required not in self.info:
                raise AttributeError(
                    "Required Attribute " + required + " missing."
                )
            if type(self.info[required]) is not attrs["required"][required]:
                raise AttributeError(
                    "Attribute " + required + " has wrong type: " +
                    str(type(self.info[required]))
                )

        # Check if any optional attributes have the correct type
        for optional in attrs["optional"]:
            if optional in self.info \
                    and type(self.info[optional]) is \
                    not attrs["optional"][optional]:
                raise AttributeError("Invalid optional attribute: " + optional)

        # Check that all extender attributes are valid parent attributes
        for extender_type in attrs["extenders"]:
            if extender_type in self.info:

                if type(self.info[extender_type]) is not dict:
                    raise AttributeError("Extender Type is not a dictionary: "
                                         + extender_type)

                # extender ~ 'Season 1'
                for extender in self.info[extender_type]:

                    if type(self.info[extender_type][extender]) \
                            is not attrs["extenders"][extender_type]:
                        raise AttributeError(
                            "Extender is not a dictionary: " + extender
                        )

                    for extender_attr in self.info[extender_type][extender]:

                        if extender_attr not in self.info:
                            raise AttributeError(
                                "Invalid attribute defined in extender: "
                                + extender_attr
                            )

                        if not isinstance(
                                self.info[extender_type][extender]
                                [extender_attr],
                                type(self.info[extender_attr])):
                            raise AttributeError(
                                "Invalid type for extender attribute: " +
                                extender_attr
                            )

        if self.media_type != self.identifier:
            raise AttributeError("Media Type Mismatch")

    def write_changes(self):
        """
        Writes the current class/instance variables to the JSON file
        :return: None
        """
        with open(self.info_file, 'w') as j:
            j.write(json.dumps(
                self.info,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            ))

    # noinspection PyMethodMayBeStatic
    def get_child_names(self) -> List[str]:
        """
        Method that fetches all children items (like Seasons, for example)
        :return: A list of children names
        """
        return []

    def get_icon_path(self, identifier: str = "") -> str or None:
        """
        Fetches the path to an icon file

        :param identifier: The identifier for the icon. Defaults to 'main'
        :return: The path to the icon file,
                 or None if there does not exist such a file
        """
        identifier = identifier \
            if identifier != "" \
            else self.child_key if self.child_key != "" else "main"
        for ext in [".png", ".jpg"]:
            iconfile = os.path.join(
                self.root_path, ".meta", "icons", identifier + ext)
            if os.path.isfile(iconfile):
                return iconfile
        return None

    # noinspection PyTypeChecker,PyDefaultArgument
    @staticmethod
    def define_attributes(additional: List[Dict[str, Dict[str, type]]]=[]) \
            -> Dict[str, Dict[str, type]]:
        """
        Defines the attributes for a media type
        :param additional: Can be used (together with super) by child classes
                           to add more attributes
        :return: A dictionary of required and optional attributes,
                 as well as identifiers for extenders
        """
        attributes = {
            "required": {"type": str, "name": str, "tags": list},
            "optional": {},
            "extenders": {}
        }
        for extra in additional:
            attributes["required"].update(extra["required"])
            attributes["optional"].update(extra["optional"])
            attributes["extenders"].update(extra["extenders"])

        return attributes
