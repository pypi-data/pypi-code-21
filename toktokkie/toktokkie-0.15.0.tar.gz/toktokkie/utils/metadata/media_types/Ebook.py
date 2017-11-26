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
from typing import Dict, List
from toktokkie.utils.metadata.media_types.Base import Base


class Ebook(Base):
    """
    Models the ebook media type
    """

    identifier = "ebook"
    """
    An identifier string that indicates the type
    """

    # Getters
    @property
    def author(self) -> str:
        return str(self.resolve_inner_attribute("author"))

    @property
    def isbn(self) -> str:  # ISBN-13
        return str(self.resolve_inner_attribute("isbn"))

    @property  # Doesn't get a setter
    def books(self) -> Dict[str, Dict[str, object]] or None:
        if self.child_key and self.extender_key:
            return None
        else:
            return self.resolve_inner_attribute("books")

    # Setters
    @author.setter
    def author(self, value: str):
        self.store_inner_attribute("author", value)

    @isbn.setter
    def isbn(self, value: str):
        self.store_inner_attribute("isbn", value)

    def get_child_names(self) -> List[str]:
        """
        Method that fetches all children items
        (The individual books, in this case)
        :return: A list of children names
        """
        children = os.listdir(self.path)
        children = list(filter(
            lambda x:
            not x.startswith(".") and
            os.path.isfile(os.path.join(self.path, x)) and
            x.endswith(".epub"),
            children
        ))
        return list(map(lambda x: x.rsplit(".epub")[0], children))

    # noinspection PyDefaultArgument
    @staticmethod
    def define_attributes(additional: List[Dict[str, Dict[str, type]]]=[]) \
            -> Dict[str, Dict[str, type]]:
        """
        Defines additional attributes for this media type
        :param additional: Further additional parameters
                           for use with child classes
        :return: The attributes of the Media Type
        """
        additional.append({
            "required": {"isbn": str},
            "optional": {},
            "extenders": {"books": dict}
        })
        return super(Ebook, Ebook).define_attributes(additional)
