# -*- coding: utf-8 -*-

from __future__ import absolute_import
from PIL import Image as PILImage

from pyfileinfo.file import File


class Image(File):
    def __init__(self, file_path):
        File.__init__(self, file_path)

        self._image = None

    def __getattr__(self, item):
        try:
            return getattr(self.image, item)
        except AttributeError:
            if item == 'resolution':
                return self.image.size

            return File.__getattr__(self, item)

    @staticmethod
    def is_valid(path):
        try:
            from PIL import Image as PILImage
            PILImage.open(path)
        except Exception:  # noqa: E722
            return False

        return True

    @property
    def image(self):
        if self._image is None:
            self._image = PILImage.open(self.path)

        return self._image

    @property
    def resolution(self):
        return self._image.size

    @staticmethod
    def hint():
        return ['.jpg', '.png', '.jpeg', '.bmp']
