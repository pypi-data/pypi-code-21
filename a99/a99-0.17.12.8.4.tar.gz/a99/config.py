"""
Gear for working with configuration files

  - subclass of `configobj.ConfigObj`
"""

from configobj import ConfigObj
import a99
import os
import re

__all__ = ["AAConfigObj", "get_config_obj"]

class AAConfigObj(ConfigObj):
    """Subclassed ConfigObj to create section structures automatically when getting/setting items"""

    def _get_section(self, path_):
        """Auto-creates section structure

        Last element in path_ is considered to be the "filename" (item name)

        Returns: (configobj.Session object, converted path)
        """

        if isinstance(path_, str):
            path_ = path_.strip().split("/")
            if path_[0] == "":
                path_ = path_[1:]

        obj = self
        for section_name in path_[:-1]:
            try:
                obj = obj[section_name]
            except KeyError:
                obj[section_name] = {}  # creates section
                obj = obj[section_name]

        return obj, path_

    def get_item(self, path_, default):
        """Returns item or default

        Arguments:
            path_ -- path to item in section/subsection structure. May be either:
                     ["section", "subsection", ...] or
                     "[/]section/subsection/..."  (leading slash is tolerated)
            default -- value to return if item is not found

        Argument 'default' is also used to determine the type of the data to return:

            - str and list: returned as retrieved
            - int and float: eval'ed
            - bool: parsed
        """
        section, path_ = self._get_section(path_)


        key = path_[-1]

        if key not in section:
            return default

        xvalue = section[key]
        type_ = type(default)
        if type_ in (str, list):
            return xvalue
        elif type_ == bool:
            value = True if xvalue == "True" else False if xvalue == "False" else eval(xvalue)
        elif type_ in (int, float):
            value = type_(xvalue)
        else:
            raise TypeError("Type not supported: {}".format(type_.__name__))
        return value


    def set_item(self, path_, value):
        """Sets item and automatically saves file"""
        section, path_ = self._get_section(path_)
        section[path_[-1]] = value
        self.write()


def get_config_obj(filename):
    """Reads/creates filename at user **home** folder and returns a AAConfigObj object"""

    if not filename.startswith("."):
        a99.get_python_logger().warning("Configuration filename '{}' does not start with a '.'".format(filename))

    path_ = os.path.join(os.path.expanduser("~"), filename)
    return AAConfigObj(path_, encoding="UTF8")
