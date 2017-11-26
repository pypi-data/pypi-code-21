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

import webbrowser
from toktokkie.ui.qt.widgets.common_config import GenericConfig
from toktokkie.ui.qt.pyuic.tv_series_config import Ui_TvSeriesConfig


class TvSeriesConfig(GenericConfig, Ui_TvSeriesConfig):

    """
    Widget for a TV Series
    """

    def __init__(self, parent):
        """
        Initializes the widget
        :param parent: The window in which to display the widget
        """
        super().__init__(parent)
        self.setupUi(self)
        self.metadata = None
        self.initialize()
        self.tvdb_url_button.clicked.connect(
            lambda x: webbrowser.open(self.metadata.tvdb_url, new=2))

    def load_online_data(self):
        """
        Downloads data from tvdb.com and displays the data afterwards
        :return: None
        """
        metadata_name = self.metadata.name

        self.first_aired_label.setText("")
        self.episode_length_label.setText("")
        self.amount_of_episodes_label.setText("")
        self.amount_of_seasons_label.setText("")
        self.genres_label.setText("")

        tvdb_data = self.metadata.load_tvdb_data()

        # Make sure that the same metadata object is still being displayed
        if metadata_name == self.metadata.name:
            self.first_aired_label.setText(tvdb_data["firstaired"])
            self.episode_length_label.setText(tvdb_data["runtime"])
            self.amount_of_episodes_label.setText(
                str(tvdb_data["episode_count"]))
            self.amount_of_seasons_label.setText(
                str(tvdb_data["season_count"]))
            self.genres_label.setText(", ".join(tvdb_data["genres"]))
