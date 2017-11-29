# -*- coding: utf-8 -*-

import os
import shutil
import time

import requests
import click

from .mangastream import chapter_number_pages, image_url

all = ['downloader']


class Downloader(object):
    """The Manga Downloader.

    Attributes
    ----------
    DOWNLOAD_DIRECTORY : str
        Where to download mangas
    """
    DOWNLOAD_DIRECTORY = os.path.expanduser('~/Desktop')

    def create_manga_directory(self, manga_name, chapter_number):
        """Create the manga directory with the name and the number.

        Parameters
        ----------
        manga_name : str
            the manga name
        chapter_number : str
            the chapter number

        Returns
        -------
        str
            the manga directory path
        """
        chapter_dir = "{0}-{1}".format(manga_name, chapter_number)
        path = "/".join([self.DOWNLOAD_DIRECTORY, chapter_dir])
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        return path

    @staticmethod
    def build_image_path(chapter_dir, manga, chapter, image):
        """Build the image path based.

        Parameters
        ----------
        chapter_dir : str
            the manga dir path
        manga : str
            the manga name
        chapter : str
            the chapter number
        image : str
            the image name

        Returns
        -------
        str
            the full image path
        """
        image_name = "{0}-{1}-{2}.jpg".format(manga, chapter, image)
        image_path = "/".join([chapter_dir, image_name])
        return image_path

    def urls(self, chapter):
        """Generate tuple of the page, the url and the full image path.

        Parameters
        ----------
        chapter : dict
            contains the number of pages,
                     the chapter url,
                     the chapter directory,
                     the chapter name,
                     the chapter number

        Yields
        ------
        tuple
            the next image page, url and full image path
        """
        for n in range(chapter['pages']):
            page = str(n + 1)
            url = '/'.join([chapter['url'], page])
            url = "http://{0}".format(image_url(url))
            path = self.build_image_path(chapter['dir'],
                                         chapter['name'],
                                         chapter['chapter'],
                                         page)

            yield (page, url, path)

    def process_arguments(self, kwargs):
        """Return a dict of the arguments.
        """
        chapter_name = kwargs['manga']
        chapter_number = kwargs['chapter']
        chapter_url = kwargs['url'].rsplit('/', 1)[0]
        chapter_dir = self.create_manga_directory(chapter_name, chapter_number)
        chapter_pages = chapter_number_pages(chapter_url)

        return {
            'name': chapter_name,
            'chapter': chapter_number,
            'url': chapter_url,
            'dir': chapter_dir,
            'pages': chapter_pages,
        }

    def download_image(self, image_url, image_path):
        """Download an image

        Parameters
        ----------
        image_url : str
            the image's source
        image_path : str
            the image's destination


        Returns
        -------
        int
            0 if ok else 1
        """
        r = requests.get(image_url)
        if r.status_code == 200:
            with open(image_path, 'wb') as f:
                f.write(r.content)
            return 0
        else:
            return 1

    def download(self, progress=False, **kwargs):
        """Download a chapter

        Parameters
        ----------
        progress : bool
            True if you want a progress bar
        **kwargs
            Must have : name, chapter, url, dir, pages.
        """
        chapter = self.process_arguments(kwargs)

        if not progress:

            for page, url, path in self.urls(chapter):
                print("  Page {0} -> {1}".format(page, path))
                self.download_image(url, path)
        else:

            with click.progressbar(self.urls(chapter),
                                   length=chapter['pages'],
                                   label=chapter['name']) as pbar:
                for page, url, path in pbar:
                    self.download_image(url, path)
                    pbar.update(1)
                    # Be gentle with mangastream
                    time.sleep(0.1)


downloader = Downloader()
