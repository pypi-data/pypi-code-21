#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import cryio


class Background:
    def __init__(self):
        self._bkg = None
        self._bkg_checksum = 0
        self._bkg_coef = 1

    def init(self, files, dark=None, normalize=None, coefficient=1.0, flatfield=None):
        if files:
            checksum = binascii.crc32(''.join(files).encode())
            res = checksum == self._bkg_checksum
            self._bkg_checksum = checksum
            if res and self._bkg_coef == coefficient:
                return
            self._bkg = None
            for image in files:
                try:
                    bkg = cryio.openImage(image)
                except OSError:
                    continue
                bkg.float()
                if dark:
                    bkg = dark(bkg)
                if normalize:
                    bkg = normalize(bkg)
                if self._bkg is None:
                    self._bkg = bkg
                elif self._bkg.array.shape == bkg.array.shape:
                    self._bkg.array += bkg.array
                    self._bkg.transmission += bkg.transmission
                    self._bkg.photo += bkg.photo
            if self._bkg is not None:
                if flatfield:
                    self._bkg = flatfield(self._bkg)
                self._bkg.array *= float(coefficient / len(files))
                self._bkg.transmission /= float(len(files))
                self._bkg.photo /= float(len(files))
                self._bkg_coef = coefficient
        else:
            self._bkg = None
            self._bkg_checksum = 0
            self._bkg_coef = 1

    def __call__(self, image, transmission=False, thick=1, concen=0, halina=False):
        tc = 0
        if self._bkg is not None and self._bkg.array.shape == image.array.shape:
            if transmission and image.transmission and self._bkg.transmission:
                tc = image.transmission / self._bkg.transmission
                if halina:
                    image.array = (image.array / image.photo - self._bkg.array / self._bkg.photo) * tc / thick
                else:
                    image.array = (image.array - self._bkg.array * (1 - concen) * tc) / image.transmission / thick
            else:
                image.array = image.array.astype(float) - self._bkg.array
        image.transmission_coefficient = tc
        return image
