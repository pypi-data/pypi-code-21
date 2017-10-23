#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import cbfimage
from . import edfimage
from . import fit2dmask
from . import mar345image
from . import numpymask
from . import brukerimage
from .cryioimage import ImageError, CryioError


__openable = (
    cbfimage.CbfImage,
    edfimage.EdfImage,
    fit2dmask.Fit2DMask,
    mar345image.Mar345Image,
    numpymask.NumpyMask,
    brukerimage.BrukerImage
)


def imageext():
    for cls in __openable:
        for ext in cls.Extensions:
            yield cls, ext


def extensions():
    for cls, ext in imageext():
        yield ext


def openImage(filename):
    for cls, ext in imageext():
        if filename.endswith(ext):
            return cls(filename)
    raise ImageError(f'CryIO could not recognize the image {filename}')


open_image = openImage
