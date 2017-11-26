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

import time
import webbrowser
from toktokkie.ui.qt.widgets.common_config import GenericConfig
from toktokkie.ui.qt.pyuic.anime_series_config import Ui_AnimeSeriesConfig


class AnimeSeriesConfig(GenericConfig, Ui_AnimeSeriesConfig):

    """
    Widget for a Anime Series
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
            lambda x: webbrowser.open(self.metadata.tvdb_url, new=2)
        )
        self.myanimelist_url_button.clicked.connect(
            lambda x: webbrowser.open(self.metadata.myanimelist_url, new=2)
        )

    def load_online_data(self):
        """
        Downloads data from myanimelist.net and displays the data afterwards
        :return: None
        """
        metadata_name = self.metadata.name

        self.mal_type_label.setText("")
        self.mal_episodes_label.setText("")
        self.mal_status_label.setText("")
        self.mal_aired_label.setText("")
        self.mal_studios_label.setText("")
        self.mal_source_label.setText("")
        self.mal_genres_label.setText("")
        self.mal_runtime_label.setText("")
        self.mal_score_label.setText("")
        self.mal_ranking_label.setText("")

        # Wait for 0.2 seconds before downloading data,
        # stop thread if metadata has changed before doing so
        time.sleep(0.2)
        if metadata_name != self.metadata.name:
            return

        mal_data = self.metadata.load_myanimelist_data()

        # Make sure that the same metadata object is still being displayed
        if metadata_name == self.metadata.name:
            self.mal_type_label.setText(mal_data["type"])
            self.mal_episodes_label.setText(str(mal_data["episodes"])
                                            if mal_data["episodes"] != -1
                                            else "?")
            self.mal_status_label.setText(mal_data["status"])
            self.mal_aired_label.setText(mal_data["aired"])
            self.mal_studios_label.setText(", ".join(mal_data["studios"]))
            self.mal_source_label.setText(mal_data["source"])
            self.mal_genres_label.setText(", ".join(mal_data["genres"]))
            self.mal_runtime_label.setText(mal_data["runtime"])
            self.mal_score_label.setText(mal_data["score"])
            self.mal_ranking_label.setText(mal_data["rank"])
