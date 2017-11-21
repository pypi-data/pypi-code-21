####################################################################################################
#
# SimpleMorphoMath - A simple mathematical morphology library.
# Copyright (C) 2012 Salvaire Fabrice
#
####################################################################################################

""" This module implements Morphological 2D Operators.
"""

####################################################################################################

import itertools
import numpy as np

####################################################################################################

from SimpleMorphoMath.SimpleMorphoMath1D import *

####################################################################################################

class Location(object):

    ###############################################

    def __init__(self, *args):

        array = self._check_arguments(args)
        self.array = np.array(array)
        if self.array.size != 2 or self.array.ndim != 1:
            raise ValueError("Wrong shape")

    ###############################################

    def _check_arguments(self, args):

        size = len(args)
        if size == 1:
            array = args[0]
        elif size == 2:
            array = args
        else:
            raise ValueError("Args size > 2")

        return array

    ###############################################

    def __len__(self):

        # used by np.arrray when __init__ args is a Location instance
        return 2

    ###############################################

    def _get_x(self):

        return self.array[0]

    def _get_y(self):

        return self.array[1]

    x = property(_get_x, None, None, None)
    y = property(_get_y, None, None, None)

    ###############################################

    def __str__(self):

        return 'Location (%i, %i)' % (self.x, self.y)

    ###############################################

    def __getitem__(self, index):

        return self.array[index]

    ###############################################

    def __add__(self, other):

        return Location(self.array + other.array)

    ###############################################

    def __eq__(self, other):

        return self.x == other.x and self.y == other.y

####################################################################################################

class Domain2D(object):

    ###############################################

    def __init__(self, x, y):

        self.x = Domain(x.inf, x.sup)
        self.y = Domain(y.inf, y.sup)

    ###############################################

    def forward_iterator(self):

        for location in itertools.product(self.x.forward_iterator(), self.y.forward_iterator()):
            yield Location(location)

    ###############################################

    def backward_iterator(self):

        for location in itertools.product(self.x.backward_iterator(), self.y.backward_iterator()):
            yield Location(location)

    ###############################################

    def __contains__(self, location):

        return location.x in self.x and location.y in self.y

####################################################################################################

class BallStructuringElement(StructuringElement):

    # Fixme: ???

    ###############################################

    def __init__(self, radius):

        # generate (-1, 0, 1)
        axis_offsets = range(-radius, radius +1)
        # generate (-1, 0, 1) * (-1, 0, 1)
        #   (-1, -1), (-1, 0), (-1, 1),
        #   ( 0, -1), ( 0, 0), ( 0, 1),
        #   ( 1, -1), ( 1, 0), ( 1, 1)
        offset = [Location(x, y) for x, y in itertools.product(axis_offsets, axis_offsets)]
        super(BallStructuringElement, self).__init__(offset)

####################################################################################################

class CrossStructuringElement(StructuringElement):

    ###############################################

    def __init__(self, radius):

        offset = \
            [Location(0, y) for y in range(-radius, 0)] + \
            [Location(x, 0) for x in range(-radius, radius +1)] + \
            [Location(0, y) for y in range(1, radius +1)]
        super(CrossStructuringElement, self).__init__(offset)

####################################################################################################

class HLineStructuringElement(StructuringElement):

    ###############################################

    def __init__(self, radius):

        offset = [Location(0, y) for y in range(-radius, radius +1)]
        super(HLineStructuringElement, self).__init__(offset)

####################################################################################################

class VLineStructuringElement(StructuringElement):

    ###############################################

    def __init__(self, radius):

        offset = [Location(x, 0) for x in range(-radius, radius +1)]
        super(VLineStructuringElement, self).__init__(offset)

####################################################################################################

unit_ball = BallStructuringElement(1)
cross = CrossStructuringElement(1)

####################################################################################################

class Function2D(Function):

    unit_ball = BallStructuringElement(1)

    ###############################################

    def __init__(self, values):

        self.values = np.array(values, dtype=np.int)
        shape = self.values.shape
        self.domain = Domain2D(Domain(inf=0, sup=shape[0] -1),
                               Domain(inf=0, sup=shape[1] -1))

    ###############################################

    def __array__(self, dtype):

        # used to pass Function2D as argument to the ctor

        if dtype != self.values.dtype:
            raise NotImplementedError

        return self.values

    ###############################################

    def _zeros(self):

        return np.zeros(self.values.shape, dtype=np.uint)

    ###############################################

    def __getitem__(self, location):

        return self.values[location.x,location.y]

    ###############################################

    def __setitem__(self, location, value):

        self.values[location.x,location.y] = value

    ###############################################

    def translate(self, offset, padd_inf=True):

        new_values = self._zeros()

        if offset == Location(0, 0):
            new_values[...] = self.values[...]
        else:
            if padd_inf:
                padd_value = 0
            else:
                padd_value = self.max()

            # Fixme: find a simplest way do to that

            if offset.x < 0 and offset.y < 0:
                new_values[offset.x:,offset.y:] = padd_value
                new_values[:offset.x,:offset.y] = self.values[-offset.x:,-offset.y:]

            elif offset.x == 0 and offset.y < 0:
                new_values[:,offset.y:] = padd_value
                new_values[:,:offset.y] = self.values[:,-offset.y:]

            elif offset.x > 0 and offset.y < 0:
                new_values[:offset.x,offset.y:] = padd_value
                new_values[offset.x:,:offset.y] = self.values[:-offset.x,-offset.y:]

            elif offset.x < 0 and offset.y > 0:
                new_values[offset.x:,:offset.y] = padd_value
                new_values[:offset.x,offset.y:] = self.values[-offset.x:,:-offset.y]

            elif offset.x == 0 and offset.y > 0:
                new_values[:,:offset.y] = padd_value
                new_values[:,offset.y:] = self.values[:,:-offset.y]

            elif offset.x > 0 and offset.y > 0:
                new_values[:offset.x,:offset.y] = padd_value
                new_values[offset.x:,offset.y:] = self.values[:-offset.x,:-offset.y]

            if offset.x < 0 and offset.y == 0:
                new_values[offset.x:,:] = padd_value
                new_values[:offset.x,:] = self.values[-offset.x:,:]

            elif offset.x > 0 and offset.y == 0:
                new_values[:offset.x,:] = padd_value
                new_values[offset.x:,:] = self.values[:-offset.x,:]

        self.values = new_values

        return self

    ###############################################

    def print_object(self):

        print(str(self.values).replace('0', '-'))

    ###############################################

    def reconstruct_using_fifo(self, marker, verbose=False):

        """ Gray Scale Reconstruction Algorithm using FIFO from Luc Vincent
        """

        reconstruction = marker.clone()

        structuring_element_iterator = StructuringElementIterator(self.unit_ball, self.domain)

        def dilate(p, sub_domain):
            reconstruction[p] = min(max([reconstruction[q] for q in structuring_element_iterator.iterate_at(p, sub_domain)]), self[p])

        # Propagate marker forward in self
        for i in self.domain.forward_iterator():
            dilate(i, '+')

        if verbose:
            print('N+')
            reconstruction.print_object()
            for p in self.domain.backward_iterator():
                dilate(p, '-')
            print('N-')
            reconstruction.print_object()

        # Propagate marker backward in self and fill the fifo for the missed points
        fifo = []
        for p in self.domain.backward_iterator():
            dilate(p, '-')
            # If a point in the N- has to be dilated then push it in the fifo
            for q in structuring_element_iterator.iterate_at(p, '-'):
                if reconstruction[q] < reconstruction[p] and reconstruction[q] < self[q]:
                    fifo.append(p)
                    continue

        # Consume the fifo
        while len(fifo):
            # pop fifo
            p, fifo = fifo[0], fifo[1:]
            # dilate the current point in self and push the new point
            for q in structuring_element_iterator.iterate_at(p):
                if reconstruction[q] < reconstruction[p] and reconstruction[q] != self[q]:
                    reconstruction[q] = min(reconstruction[p], self[q])
                    fifo.append(q)

        return reconstruction
