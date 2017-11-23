"""
Copyright 2015-2017 Hermann Krumrey

This file is part of manga-dl.

manga-dl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

manga-dl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with manga-dl.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
from typing import List
from manga_dl.entities.MangaVolume import MangaVolume


class GenericMangaScraper(object):
    """
    Class that models how a Manga Scraper should operate
    """

    @staticmethod
    def url_match(manga_url: str) -> bool:
        """
        Checks if a URL matches the pattern expected by the scraper

        :param manga_url: the URL to check
        :return: True if it matches, False otherwise
        """
        raise NotImplementedError()

    @staticmethod
    def get_series_name(manga_url: str) -> str:
        """
        Parses the URL to determine the series name

        :param manga_url: The URL to parse
        :return:          The series name
        """
        raise NotImplementedError()

    @staticmethod
    def scrape_volumes_from_url(manga_url: str, manga_directory: str,
                                skip_existing_chapters: bool = False,
                                max_threads: int = 1, verbose: bool = False) \
            -> List[MangaVolume]:
        """
        Scrapes a given URL

        :param manga_url: the given URL to scrape
        :param manga_directory: the manga directory,
                                which can be used to skip existing chapters
        :param skip_existing_chapters: Flag that can be set to skip existing
                                       chapters,
                                       thereby increasing scraping speed
        :param max_threads: the maximum numbers of threads to use
        :param verbose: Sets the verbosity flag. Defaults to no output
        :return: a list of volumes, which should also contain chapters
        """
        raise NotImplementedError()
