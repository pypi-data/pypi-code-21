u"""
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

from __future__ import absolute_import
import os
from typing import Dict, List
from toktokkie.utils.metadata.media_types.Base import Base
from itertools import ifilter
from itertools import imap


class Ebook(Base):
    u"""
    Models the ebook media type
    """

    identifier = u"ebook"
    u"""
    An identifier string that indicates the type
    """

    # Getters
    @property
    def author(self):
        return unicode(self.resolve_inner_attribute(u"author"))

    @property
    def isbn(self):  # ISBN-13
        return unicode(self.resolve_inner_attribute(u"isbn"))

    @property  # Doesn't get a setter
    def books(self):
        if self.child_key and self.extender_key:
            return None
        else:
            return self.resolve_inner_attribute(u"books")

    # Setters
    @author.setter
    def author(self, value):
        self.store_inner_attribute(u"author", value)

    @isbn.setter
    def isbn(self, value):
        self.store_inner_attribute(u"isbn", value)

    def get_child_names(self):
        u"""
        Method that fetches all children items
        (The individual books, in this case)
        :return: A list of children names
        """
        children = os.listdir(self.path)
        children = list(ifilter(
            lambda x:
            not x.startswith(u".") and
            os.path.isfile(os.path.join(self.path, x)) and
            x.endswith(u".epub"),
            children
        ))
        return list(imap(lambda x: x.rsplit(u".epub")[0], children))

    # noinspection PyDefaultArgument
    @staticmethod
    def define_attributes(additional=[]):
        u"""
        Defines additional attributes for this media type
        :param additional: Further additional parameters
                           for use with child classes
        :return: The attributes of the Media Type
        """
        additional.append({
            u"required": {u"isbn": unicode},
            u"optional": {},
            u"extenders": {u"books": dict}
        })
        return super(Ebook, Ebook).define_attributes(additional)
