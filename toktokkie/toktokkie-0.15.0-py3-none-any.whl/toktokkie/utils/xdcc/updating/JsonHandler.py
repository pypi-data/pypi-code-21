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

# imports
import sys
import json
from typing import List
from toktokkie.utils.xdcc.updating.objects.Series import Series, \
    from_dict as series_generator


class JsonHandler(object):
    """
    Class that handles storing and loading JSON configs for the XDCC Updater
    """

    def __init__(self, json_file: str = None) -> None:
        """
        Creates a new JsonHandler, either from scratch or
        from an existing JSON file

        :raises:          ValueError if the loaded JSON file was invalid.json
        :param json_file: An optional JSON file location.
        """
        self.json_data = []
        self.json_location = None

        if json_file is not None:
            self.json_location = json_file
            with open(json_file, 'r') as f:
                self.json_data = json.load(f)
        self.check_validity()

    def check_validity(self) -> None:
        """
        Checks the JSON data for validity. If the file is not valid,
        an exception is raised

        :raises: ValueError if the loaded JSON file was invalid.json
        :return: None
        """

        try:
            for series in self.json_data:
                for check in ["destination_directory",
                              "search_name",
                              "quality_identifier",
                              "bot_preference",
                              "season",
                              "search_engines",
                              "naming_scheme",
                              "search_pattern"]:
                    if check not in series.keys():
                        raise ValueError()
        except AttributeError:
            raise ValueError()

    def store_json(self, destination: str = "") -> None:
        """
        Stores the current JSON data in a JSON file

        :param destination: The destination JSON file. If left blank,
        the loaded file will be used
        :return:            None
        """
        if not destination:
            destination = self.json_location

        self.json_location = destination

        open_mode = "w" if sys.version_info[0] >= 3 else 'wb'

        with open(destination, open_mode) as f:
            json.dump(
                self.json_data,
                f,
                sort_keys=True,
                indent=2,
                separators=(',', ': ')
            )

    def add_series(self, series: Series) -> None:
        """
        Adds a Series to the JSON Data

        :param series:
        :return:
        """
        self.json_data.append(series.to_dict())

    def remove_series(self, series: Series) -> None:
        """
        Removes a series from the JSON Data

        :param series: The series to remove
        :return:       None
        """
        pop_index = None
        for i, show in enumerate(self.json_data):
            if series.is_same(show):
                pop_index = i

        if pop_index is not None:
            self.json_data.pop(pop_index)

    def get_series(self) -> List[Series]:
        """
        Generates Series objects from the JSON data

        :return: The List of Series
        """
        series = []
        for data in self.json_data:
            series.append(series_generator(data))
        return series

    def get_json_file_path(self) -> str:
        """
        :return: The path to the internal JON file
        """
        return self.json_location if self.json_location is not None else ""
