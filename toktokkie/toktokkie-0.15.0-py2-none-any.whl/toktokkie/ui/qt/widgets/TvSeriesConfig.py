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
import webbrowser
from toktokkie.ui.qt.widgets.common_config import GenericConfig
from toktokkie.ui.qt.pyuic.tv_series_config import Ui_TvSeriesConfig


class TvSeriesConfig(GenericConfig, Ui_TvSeriesConfig):

    u"""
    Widget for a TV Series
    """

    def __init__(self, parent):
        u"""
        Initializes the widget
        :param parent: The window in which to display the widget
        """
        super(TvSeriesConfig, self).__init__(parent)
        self.setupUi(self)
        self.metadata = None
        self.initialize()
        self.tvdb_url_button.clicked.connect(
            lambda x: webbrowser.open(self.metadata.tvdb_url, new=2))

    def load_online_data(self):
        u"""
        Downloads data from tvdb.com and displays the data afterwards
        :return: None
        """
        metadata_name = self.metadata.name

        self.first_aired_label.setText(u"")
        self.episode_length_label.setText(u"")
        self.amount_of_episodes_label.setText(u"")
        self.amount_of_seasons_label.setText(u"")
        self.genres_label.setText(u"")

        tvdb_data = self.metadata.load_tvdb_data()

        # Make sure that the same metadata object is still being displayed
        if metadata_name == self.metadata.name:
            self.first_aired_label.setText(tvdb_data[u"firstaired"])
            self.episode_length_label.setText(tvdb_data[u"runtime"])
            self.amount_of_episodes_label.setText(
                unicode(tvdb_data[u"episode_count"]))
            self.amount_of_seasons_label.setText(
                unicode(tvdb_data[u"season_count"]))
            self.genres_label.setText(u", ".join(tvdb_data[u"genres"]))
