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
import time
import webbrowser
from toktokkie.ui.qt.widgets.common_config import GenericConfig
from toktokkie.ui.qt.pyuic.light_novel_config import Ui_LightNovelConfig


class LightNovelConfig(GenericConfig, Ui_LightNovelConfig):
    u"""
    Widget for a Light Novel
    """

    def __init__(self, parent):
        u"""
        Initializes the widget
        :param parent: The window in which to display the widget
        """
        super(LightNovelConfig, self).__init__(parent)
        self.setupUi(self)
        self.metadata = None
        self.initialize()
        self.myanimelist_url_button.clicked.connect(
            lambda x: webbrowser.open(self.metadata.myanimelist_url, new=2))
        self.novelupdates_url_button.clicked.connect(
            lambda x: webbrowser.open(self.metadata.novelupdates_url, new=2))

    def load_online_data(self):
        u"""
        Downloads data from myanimelist.net and novelupdates.com and
        displays the data afterwards.
        :return: None
        """
        metadata_name = self.metadata.name

        self.volume_count_label.setText(u"")
        self.status_label.setText(u"")
        self.published_label.setText(u"")
        self.genres_label.setText(u"")
        self.licensed_label.setText(u"")
        self.fully_translated_label.setText(u"")
        self.mal_score_label.setText(u"")
        self.mal_ranking_label.setText(u"")

        # Wait for 0.2 seconds before downloading data,
        # stop thread if metadata has changed before doing so
        time.sleep(0.2)
        if metadata_name != self.metadata.name:
            return

        mal_data = self.metadata.load_myanimelist_data()
        novelupdates_data = self.metadata.load_novelupdates_data()

        # Make sure that the same metadata object is still being displayed
        if metadata_name == self.metadata.name:
            self.volume_count_label.setText(unicode(mal_data[u"volumes"])
                                            if mal_data[u"volumes"] != -1
                                            else u"?")
            self.status_label.setText(mal_data[u"status"])
            self.published_label.setText(mal_data[u"published"])
            self.genres_label.setText(u", ".join(mal_data[u"genres"]))
            self.licensed_label.setText(novelupdates_data[u"licensed"])
            self.fully_translated_label.setText(
                novelupdates_data[u"completely_translated"]
            )
            self.mal_score_label.setText(mal_data[u"score"])
            self.mal_ranking_label.setText(mal_data[u"rank"])
