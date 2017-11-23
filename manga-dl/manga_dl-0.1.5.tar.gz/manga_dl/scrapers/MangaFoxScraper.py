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
import os
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
from multiprocessing import Pool

from manga_dl.scrapers.GenericMangaScraper import GenericMangaScraper
from manga_dl.entities.MangaChapter import MangaChapter
from manga_dl.entities.MangaPage import MangaPage
from manga_dl.entities.MangaVolume import MangaVolume


class MangaFoxScraper(GenericMangaScraper):
    """
    Class that models how a Manga Scraper should operate
    """

    @staticmethod
    def parse_page(options: Tuple[int, bool, str]) -> MangaPage:
        """
        Parses a single page of a chapter. Can be run in parallel using
        multiprocessing.Pool, which is the reason why the arguments are all
        passed via a single Tuple, due to the limitations of Pool.map()

        :param options: the options for the page to parse:
                        image_number: The image number of the image page
                                      to parse
                        verbose: Enabling or disabling verbose output
                        chapter_base_url: The base URL of the chapter
        :return: the scraped manga page object
        """

        image_number, verbose, chapter_base_url = options
        image_page_url = chapter_base_url + "/" + str(image_number) + ".html"

        # When using multiple threads, sometimes 503 errors occur,
        # which is why we try until we succeed!
        result = requests.get(image_page_url)
        while result.status_code != 200:
            result = requests.get(image_page_url)

        image_html = result.text
        image_soup = BeautifulSoup(image_html, "html.parser")

        if len(str(image_soup)) == 204:
            print(image_soup)
            raise Exception

        image = image_soup.select("img")[0]
        image_url = str(image).split("src=\"")[1].split("\"")[0]
        image_url = image_url.replace("amp;", "")

        return MangaPage(image_number, image_url)

    @staticmethod
    def get_series_name(manga_url: str) -> str:
        """
        Returns the very end of the URL, as this is the name of the series

        :param manga_url: The URL to parse
        :return:          The series name
        """
        series_name = manga_url.rsplit("/", 1)[1].title().replace("_", " ")
        if not series_name:
            series_name = manga_url.rsplit("/", 2)[1].title().replace("_", " ")
        return series_name.title()

    @staticmethod
    def url_match(manga_url: str) -> bool:
        """
        Checks if a URL matches the pattern expected by the scraper

        :param manga_url: the URL to check
        :return: True if it matches, False otherwise
        """
        return manga_url.startswith("http://mangafox.me")

    @staticmethod
    def scrape_volumes_from_url(manga_url: str, manga_directory: str,
                                skip_existing_chapters: bool = False,
                                max_threads: int = 1, verbose: bool = False) \
            -> List[MangaVolume]:
        """
        Scrapes a given URL from mangafox.me

        :param manga_url: the given URL to scrape
        :param manga_directory: the manga directory,
                                which can be used to skip existing chapters
        :param skip_existing_chapters: Flag that can be set to skip existing
                                       chapters,
                                       thereby increasing scraping speed
        :param max_threads: The maximum amount of threads that can be used
        :param verbose: Sets the verbosity flag. Defaults to no output
        :return: a list of volumes, which should also contain chapters
        """
        html = requests.get(manga_url).text
        soup = BeautifulSoup(html, "html.parser")
        volumes = soup.select(".chlist")

        # Find the highest volume number
        # Sometimes a 'Volume 00' exists,
        # which then results in us having to decrement the highest number by 1
        volume_number = len(volumes)
        if "\"Volume 00\"" in html:
            volume_number -= 1

        volume_objects = []

        for volume in volumes:
            if verbose:
                print("Scraping Volume " + str(volume_number))

            chapters = volume.select(".tips")

            chapter_objects = []

            for chapter in chapters:
                chapter_start_url = \
                    str(chapter).split("href=\"")[1].split("\"")[0]
                chapter_base_url = chapter_start_url.rsplit("/", 1)[0]
                chapter_number = float(chapter.text.rsplit(" ", 1)[1])

                if chapter_number.is_integer():
                    formatted_chapter_number = \
                        str(int(chapter_number)).zfill(3)
                else:
                    pre_dot, post_dot = str(chapter_number).split(".")
                    formatted_chapter_number =\
                        pre_dot.zfill(3) + "." + post_dot

                chapter_directory = os.path.join(
                    manga_directory,
                    "Volume " + str(volume_number).zfill(2)
                )
                chapter_directory = os.path.join(
                    chapter_directory,
                    "Chapter " + formatted_chapter_number
                )

                if verbose:
                    print("Scraping Chapter " + str(chapter_number))

                chapter_html = requests.get(chapter_start_url).text
                chapter_soup = BeautifulSoup(chapter_html, "html.parser")
                page_amount = int(str(
                    chapter_soup.select(".l")[0])
                                  .rsplit("of ", 1)[1]
                                  .split("\t", 1)[0]
                                  )  # Don't ask

                if os.path.isdir(chapter_directory) and skip_existing_chapters:
                    if page_amount == len(os.listdir(chapter_directory)):
                        if verbose:
                            print("Skipping Chapter " +
                                  formatted_chapter_number)
                        continue

                poolsize = page_amount if page_amount < max_threads \
                    else max_threads

                threadpool = Pool(processes=poolsize)
                page_arguments = []

                for number in range(1, page_amount + 1):
                    page_arguments.append((number, verbose, chapter_base_url))

                page_objects = threadpool.map(
                    MangaFoxScraper.parse_page,
                    page_arguments
                )

                # Waits for threads to finish
                threadpool.close()
                threadpool.join()

                chapter_objects.append(MangaChapter(
                    chapter_number,
                    page_objects
                ))

            volume_objects.append(MangaVolume(volume_number, chapter_objects))
            volume_number -= 1

        return volume_objects
