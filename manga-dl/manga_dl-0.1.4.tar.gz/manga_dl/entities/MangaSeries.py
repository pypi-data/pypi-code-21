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
import shutil
import requests
from typing import Tuple
from multiprocessing import Pool
from manga_dl.scrapers.MangaScraperManager import MangaScraperManager


class MangaScraperNotFoundError(Exception):
    """
    Exception raised when no applicable manga scraper was found
    """


class MangaSeries(object):
    """
    Class that models a Manga series. It is the entry point for all operations
    related to downloading, repairing and zipping manga series.

    It offers an automatic scraper detection system that tries to find a
    fitting scraper for the URL provided
    """

    url = ""
    """
    The manga series' URL
    """

    root_directory = ""
    """
    The root directory of the downloaded manga
    """

    scraper = None
    """
    The scraper used to find the volumes belonging to the series
    """

    volumes = []
    """
    List of volumes of the series
    """

    verbose = False
    """
    Flag that can be set to enable console output
    """

    dry_run = False
    """
    Flag that can be set to disable any changes to the system,
    i.e. a dry run akin to the rsync dry run flag '-n'
    """

    max_threads = 1
    """
    Defines the maximum number of concurrent threads while scraping
    """

    def __init__(self, url: str, root_directory: str) -> None:
        """
        Initializes the Manga series

        :param url: the URL for where to look for volumes to scrapers
        :param root_directory: the directory in which the local copy of the
                               series resides in
        :raises: MangaScraperNotFound, if no applicable manga scraper was found
        """

        self.url = url
        self.root_directory = root_directory

        # Automatically find the correct scraper
        self.scraper = MangaScraperManager.get_scraper_for(url)

        if self.scraper is None:
            raise MangaScraperNotFoundError()

    def scrape(self, skip_existing_chapters: bool = False) -> None:
        """
        Finds a list of all volumes using the scraper found in the __init__
        method.

        :param skip_existing_chapters: Can be set to skip existing chapters
        :return: None
        """
        if self.scraper is not None and len(self.volumes) == 0:
            self.volumes = self.scraper.scrape_volumes_from_url(
                self.url,
                self.root_directory,
                skip_existing_chapters=skip_existing_chapters,
                max_threads=self.max_threads,
                verbose=self.verbose
            )

    def download_manga(self, update: bool = False, repair: bool = False):
        """
        Starts downloading the manga series

        :param update: flag to set an update process,
                       i.e. only downloads files that don't exist
        :param repair: flag to set a repair process,
                       i.e. updates + checks if files are OK
        :return: None
        """
        if self.verbose:
            print("Scraping " + self.url)

        if update:
            self.scrape(skip_existing_chapters=True)
        else:
            self.scrape()

        if not self.dry_run and not os.path.isdir(self.root_directory):
            os.makedirs(self.root_directory)

        download_parameters = []

        for volume in self.volumes:
            volume_directory = os.path.join(
                self.root_directory,
                volume.get_volume_name()
            )

            if not self.dry_run and not os.path.isdir(volume_directory):
                os.makedirs(volume_directory)

            for chapter in volume.get_chapters():
                chapter_directory = os.path.join(
                    volume_directory,
                    chapter.get_chapter_name()
                )

                if not self.dry_run and not os.path.isdir(chapter_directory):
                    os.makedirs(chapter_directory)

                for page in chapter.get_pages():
                    page_file = os.path.join(
                        chapter_directory,
                        page.get_page_name() + ".jpg"
                    )
                    download_parameters.append((page.image_url,
                                                page_file,
                                                not update,
                                                repair,
                                                self.verbose,
                                                self.dry_run))

        threadpool = Pool(self.max_threads)
        threadpool.map(MangaSeries.download_file, download_parameters)
        threadpool.close()
        threadpool.join()

    def update(self) -> None:
        """
        Updates the current directory with volumes and chapters
        that do not exist yet.

        :return: None
        """
        self.download_manga(update=True)

    def repair(self) -> None:
        """
        Updates the current directory with volumes and chapters that do not
        exist yet. While doing so, every file is checked for consistency
        and replaced if needed.

        :return: None
        """
        self.download_manga(repair=True)

    def zip(self, zip_volumes: bool = False, zip_chapters: bool = False):
        """
        Zips parts of the series together to enable reading in some manga
        readers, like ComicRack for android

        :param zip_volumes: flag to enable zipping volumes
        :param zip_chapters: flag to enable zipping chapters
        :return: None
        """

        for volume in os.listdir(self.root_directory):
            volume_dir = os.path.join(self.root_directory, volume)

            if volume.startswith("Volume ") and os.path.isdir(volume_dir):

                if zip_volumes:
                    if not self.dry_run:
                        shutil.make_archive(volume_dir, "zip", volume_dir)

                if zip_chapters:
                    for chapter in os.listdir(volume_dir):
                        chapter_dir = os.path.join(volume_dir, chapter)

                        if chapter.startswith("Chapter ") \
                                and os.path.isdir(chapter_dir):
                            if not self.dry_run:
                                shutil.make_archive(
                                    chapter_dir,
                                    "zip",
                                    chapter_dir
                                )

    def zip_chapters(self) -> None:
        """
        Zips the series by chapter

        :return: None
        """
        self.zip(zip_chapters=True)

    def zip_volumes(self) -> None:
        """
        Zips the series by volume

        :return: None
        """
        self.zip(zip_volumes=True)

    def zip_all(self) -> None:
        """
        Zips the series by Volume and then by chapter

        :return: None
        """
        self.zip(zip_volumes=True, zip_chapters=True)

    def set_verbose(self, verbose: bool = True) -> None:
        """
        Sets the verbosity flag

        :param verbose: the new value of the verbosity flag, defaults to True
        :return: None
        """
        self.verbose = verbose

    def set_dry_run(self, dry_run: bool = True) -> None:
        """
        Sets the dry_run flag

        :param dry_run: the new value of the dry_run flag, defaults to True
        :return: None
        """
        self.dry_run = dry_run

    def set_maximum_thread_amount(self, max_threads: int) -> None:
        """
        Sets the maximum amount of threads to be used

        :param max_threads: the new thread maximum
        :return: None
        """
        self.max_threads = max_threads

    @staticmethod
    def download_file(options: Tuple[str, str, bool, bool, bool, bool]) \
            -> None:
        """
        Downloads a file, can also be used to repair previously downloaded
        files. Can be run in parallel using the multiprocessing Pool class.
        This limits the function to a single parameter, a Tuple in this case

        :param options: Tuple containing the following parameters:
                            url: the file's URL
                            destination: the local destination for the file
                            overwrite_existing: flag that enables overwriting
                                                existing files
                            repair: flag that can be set to enable repair mode
                            verbose: Sets the verbosity flag
                            dry_run: Sets the dry run flag
        :return: None
        """
        url, destination, overwrite_existing, repair, verbose, dry_run = \
            options
        print("Downloading " + url)

        if not overwrite_existing and os.path.isfile(destination):
            return

        if repair:
            try:
                url_size = int(requests.head(url).headers["Content-Length"])
                file_size = os.path.getsize(destination)

                if url_size == file_size:
                    return
                elif verbose:
                    print("Local file broken, starting repair")

            except FileNotFoundError:
                if verbose:
                    print("File does not exist")
                pass

        if not dry_run:
            with open(destination, 'wb') as destination_file:
                if verbose:
                    print("Downloading " + destination)
                content = requests.get(url).content
                destination_file.write(content)
