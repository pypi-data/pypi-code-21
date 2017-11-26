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

# imports
from __future__ import absolute_import
from typing import Tuple
from toktokkie.utils.renaming.objects.TVEpisode import TVEpisode


class RenamerConfirmation(object):
    u"""
    Class that holds the renaming confirmation state of an Episode object
    """

    def __init__(self, episode):
        u"""
        Initializes A new RenamerConfirmation episode based
        on a provided Episode object

        :param episode: the episode to act as base for this object
        """

        self.episode = episode
        self.old_name = episode.get_old_name()
        self.new_name = episode.get_new_name()
        self.confirmed = False

    def get_episode(self):
        u"""
        :return: The stored episode object
        """
        return self.episode

    def get_names(self):
        u"""
        :return: A tuple of the old name, new name of the episode
        """
        return self.old_name, self.new_name

    def get_confirmed_status(self):
        u"""
        :return: The current confirmation status
        """
        return self.confirmed

    def confirm(self):
        u"""
        Confirms the renaming for this episode

        :return: None
        """
        self.confirmed = True
