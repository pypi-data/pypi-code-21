# -*- coding: utf-8 -*-

import os
import requests

from .mangastream import get_chapter_pages, get_image_url


class Downloader(object):

    DOWNLOAD_DIRECTORY = os.path.expanduser('~/Desktop/')

    def create_manga_directory(self, manga_name, chapter_number):

        chapter_dir = "{0}-{1}".format(manga_name, chapter_number)
        path = "/".join([self.DOWNLOAD_DIRECTORY, chapter_dir])
        os.makedirs(path)
        return path

    @staticmethod
    def build_image_path(chapter_dir, manga, chapter, image):

        image_name = "{0}-{1}-{2}.jpg".format(manga, chapter, image)
        image_path = "/".join([chapter_dir, image_name])
        return image_path

    def download_image(self, image_url, image_path):

        r = requests.get(image_url)
        if r.status_code == 200:
            with open(image_path, 'wb') as f:
                f.write(r.content)
            return 0
        else:
            return 1

    def download(self, **kwargs):

        manga = kwargs['manga']
        chapter = kwargs['chapter']
        chapter_url = kwargs['url'].rsplit('/', 1)[0]
        chapter_dir = self.create_manga_directory(manga, chapter)
        chapter_pages = get_chapter_pages(chapter_url)

        for n in range(1, chapter_pages + 1):
            page = str(n)
            url = '/'.join([chapter_url, page])
            real_url = get_image_url(url)
            real_url = "http://{0}".format(real_url)
            path = self.build_image_path(chapter_dir, manga, chapter, page)
            self.download_image(real_url, path)
