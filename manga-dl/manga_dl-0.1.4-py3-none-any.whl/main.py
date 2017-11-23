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
import argparse
import multiprocessing
from manga_dl.scrapers.MangaScraperManager import MangaScraperManager
from manga_dl.entities.MangaSeries import MangaSeries, \
    MangaScraperNotFoundError


def main() -> None:
    """
    Parses CLI arguments and starts the program

    :return: None
    """

    try:

        parser = argparse.ArgumentParser()
        parser.add_argument("url")
        parser.add_argument("-d", "--destination")
        parser.add_argument("-t", "--threads", type=int,
                            default=multiprocessing.cpu_count())
        parser.add_argument("-v", "--verbose", action="store_true",
                            default=False)
        parser.add_argument("--zip_chapters", action="store_true",
                            default=False)
        parser.add_argument("--zip_volumes", action="store_true",
                            default=False)
        parser.add_argument("--repair", action="store_true", default=False)
        parser.add_argument("--update", action="store_true", default=False)
        args = parser.parse_args()

        if args.url:

            series_name = \
                MangaScraperManager.get_series_name_from_url(args.url)
            destination = \
                os.path.join(os.getcwd(), series_name) if not args.destination\
                else args.destination

            series = MangaSeries(args.url, destination)
            series.set_verbose(args.verbose)
            series.set_maximum_thread_amount(args.threads)
            series.download_manga(update=args.update, repair=args.repair)
            series.zip(
                zip_chapters=args.zip_chapters,
                zip_volumes=args.zip_volumes
            )

        else:
            print(
                "No valid argument combination supplied. "
                "See --help for more details"
            )

    except MangaScraperNotFoundError:
        print("The provided URL is not supported")
    except KeyboardInterrupt:
        print("Thanks for using manga_dl!")
