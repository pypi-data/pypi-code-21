#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import numpy as np


class ImageError(ValueError):
    pass


class CryioError(ImageError):
    pass


class CryioImage:
    Extensions = ()

    def __init__(self, filepath=None):
        self.transmission = 0
        self.photo = 0
        self.header = {}
        self.filepath = filepath
        self.array = None
        self.multiframe = False

    def __iter__(self):
        yield self
        raise StopIteration

    def _check_array(self):
        if self.array is None:
            raise CryioError('Array is not set')

    def float(self):
        self._check_array()
        self.array = self.array.astype(np.float64)
        return self.array

    def __add__(self, other):
        if not isinstance(other, CryioImage) or other.array is None:
            raise CryioError(f'Object {other} is not recognized')
        self.array += other.array
        return self

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == '_map':
                continue
            # noinspection PyArgumentList
            setattr(result, k, copy.deepcopy(v, memo))
        return result
