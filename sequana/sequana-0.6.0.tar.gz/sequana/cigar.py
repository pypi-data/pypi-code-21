# -*- coding: utf-8 -*-
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
import re

"""
Note: could use pysam most probably to improve the speed.
"""

class Cigar(object):
    """

    .. doctest::

        >>> from sequana.cigar import Cigar
        >>> c = Cigar("2S30M1I")
        >>> len(c)
        33
        >>> c.items()

        >>> c = Cigar("1S1S1S1S")
        >>> c.compress()
        >>> c.cigarstring
        "4S"


    Possible CIGAR types are:

    - "M" for MATCH  (0)
    - "I" for Insertion (1)
    - "D" for deletion 2
    - "N" for reference skipped 3
    - "S" for soft clipping 4
    - "H" for hard clipping 5
    - "P" for padding
    - "=" for equal
    - "X" for diff
    - "B" for back

    .. note:: the length of the query sequence based on the CIGAR is calculated
        by adding the M, I, S, =, or X and other operations are ignored.
        source: https://stackoverflow.com/questions/39710796/infer-the-length-of-a-sequence-using-the-cigar/39812985#39812985

    :reference: https://github.com/samtools/htslib/blob/develop/htslib/sam.h
    """
    __slots__ = ['cigarstring']
    pattern = '(\d+)([A-Za-z])?'
    # could use a dictionary. would be faster
    #: valid CIGAR types
    types = "MIDNSHP=XB"
    def __init__(self, cigarstring):
        """.. rubric:: Constructor

        :param str cigarstring: the CIGAR string. 

        .. note:: the input CIGAR string validity is not checked. 
            If an unknown type is found, it is ignored generally.
            For instance, the length of 1S100Y is 1 since Y is not correct.

        """
        #: the CIGAR string attribute
        self.cigarstring = cigarstring

    def __str__(self):
        return self.cigarstring

    def __repr__(self):
        return "Cigar( {} )".format(self.cigarstring)

    def __len__(self):
        return sum([y for x,y in self._decompose() if x in "MIS=X"])

    def _decompose(self):
        # x is the type, y the number. Note the inversion in the tuple
        return ((y, int(x)) for x,y in re.findall(self.pattern, self.cigarstring))

    def as_sequence(self):
        return "".join( ( y*x for x,y in self._decompose()) ) 

    def as_dict(self):
        """Return cigar types and their count

        :return: dictionary

        Note that repeated types are added::

            >>> c = Cigar('1S2M1S')
            >>> c.as_dict()
            {"S":2,"M":2}

        """
        # !! here, we have to make sure that  duplicated letters are summed up
        from collections import defaultdict
        d = defaultdict(int)
        for letter, num in self._decompose():
            d[letter] += num
        return dict(d)

    def as_tuple(self):
        """Decompose the cigar string into tuples keeping track of repeated types

        :return: tuple

        .. doctest::

            >>> from sequana import Cigar
            >>> c = Cigar("1S2M1S")
            (('S', 1), ('M', 2), ('S', 1))

        """
        return tuple((x,y) for (x,y) in self._decompose())

    def compress(self):
        """1S1S should become 2S. inplace modification"""
        if len(set((x[0] for x,y in self._decompose()))) == len(self.as_tuple()):
            return

        data = self.as_tuple()
        newdata = [data[0]]
        for i, x in enumerate(data[1:]):
            N = len(newdata) - 1
            if newdata[N][0] == x[0]:
                newdata[N]= (x[0], newdata[N][1] + x[1] )
            else:
                newdata.append(x)
        self.cigarstring = "".join(["{}{}".format(y,x) for x,y in newdata])

    def stats(self):
        """Returns number of occurence for each type found in :attr:`types`

        ::

            >>> c = Cigar("1S2M1S")
            >>> c.stats()
            [2, 0, 0, 0, 2, 0, 0, 0, 0, 0]

        """
        data = [0] * len(self.types)
        dd = self.as_dict()
        for k, v in self.as_dict().items():
            data[self.types.index(k)] = v
        return data

