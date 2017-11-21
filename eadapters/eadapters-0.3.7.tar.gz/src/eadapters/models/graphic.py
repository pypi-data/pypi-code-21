#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EGraphic(base.EBase):

    images = appier.field(
        type = list
    )

    @classmethod
    def _build(cls, model, map):
        super(EGraphic, cls)._build(model, map)
        model["value"] = model["name"]
        for name, size in (
            ("thumbnail", 400),
            ("thumbnail_2x", 800),
            ("large", 1000),
            ("large_2x", 1000)
        ):
            name_i = name + "_image"
            model[name_i] = cls._get_image(model, size = name)
            model[name_i] = model[name_i] or cls._get_image(
                model,
                size = str(size),
                strict = False
            )

    @classmethod
    def _sizes(cls, size):
        alias = cls.SIZE_ALIAS.get(size, ())
        return [size] + list(alias)

    @classmethod
    def _get_image(cls, model, index = 1, size = "thumbnail", strict = True):
        images = cls._get_images(model, size = size)
        for image in images:
            if not image["order"] == index and strict: continue
            return image
        return None

    @classmethod
    def _get_images(cls, model, size = "thumbnail", sort = True):
        images = model.get("images", None)
        if not images: return []
        if "images" in images: images = images["images"]
        sizes = cls._sizes(size)
        _images = []
        for image in images:
            if not image or not isinstance(image, dict): continue
            if not image["size"] in sizes: continue
            _images.append(image)
        if sort: _images.sort(key = lambda item: item["order"])
        return _images

    def get_image_url(self, size):
        image = self.images[0]
        url = image.get(size, None)
        return url

    def get_image(self, index = 1, size = "thumbnail"):
        return self.__class__.get_image(self.model, index = index, size = size)

    def get_images(self, size = "thumbnail", sort = True):
        return self.__class__._get_images(self.model, size = size, sort = sort)
