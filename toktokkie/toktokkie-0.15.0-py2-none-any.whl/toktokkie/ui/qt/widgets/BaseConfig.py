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
from toktokkie.ui.qt.pyuic.base_config import Ui_BaseConfig
from toktokkie.ui.qt.widgets.common_config import GenericConfig


class BaseConfig(GenericConfig, Ui_BaseConfig):

    u"""
    Widget for a Base metadata object
    """

    def __init__(self, parent):
        u"""
        Initializes the widget
        :param parent: The window in which to display the widget
        """
        super(BaseConfig, self).__init__(parent)
        self.setupUi(self)
        self.metadata = None
        self.initialize()
