#!/usr/bin/env python

"""A set of classes for handling HiC peak calling."""

import os
import sys

import numpy
import h5py

import libraries._hic_peaks as _hic_peaks


class HiCCUPS(object):

    """
    This class calculates the HiCCUPS peak calling described by Rao et al. (2014).

    When initialized, this class creates an h5dict in which to store all data associated with this object.

    :param hic: A :class:`HiC <hifive.hic.HiC>` class object.
    :type hic: :class:`HiC <hifive.hic.HiC>`
    :param binsize: The size in basepairs to bin data into.
    :type binsize: int.
    :param pixel: The width, in bins, of the peaks to be called.
    :type pixel: int.
    :param fdr: The false discovery rate to use for correcting for multiple tests.
    :type fdr: float
    :param chroms: A list of chromosomes to perform peak calling on. If chroms is None, all chroms are used.
    :type chroms: list
    :param silent: Indicates whether to print information about function execution for this object.
    :type silent: bool.

    :attributes: * **file** (*str.*) - A string containing the name of the file passed during object creation for saving the object to.
                 * **silent** (*bool.*) - A boolean indicating whether to suppress all of the output messages.
                 * **history** (*str.*) - A string containing all of the commands executed on this object and their outcome.
    """

    def __init__(self, hic, binsize=25000, pixel=1, fdr=0.05, chroms=None, silent=False):
        """Create a HiCCUPS peak calling object."""
        self.binsize = binsize
        self.minwidth = int(round(15.0 / (binsize ** 0.5)))
        self.maxwidth = 20
        self.pixel = pixel
        self.hic = hic
        self.silent = silent
        self.minobs = 16
        if chroms is None:
            self.chroms = hic.chr2int.keys()
            self.chroms.sort()
        else:
            self.chroms = chroms
        self.scores = {}
        for chrom in self.chroms:
            self.calculate_scores(chrom)

    def calculate_scores(self, chrom):
        """Calculate the HiCCUPS score for a single chromosome.

        :param chrom: The chromosome for which scores are calculated.
        :type chrom: str.
        returns None
        """
        data, mapping = self.hic.cis_heatmap(chrom, binsize=self.binsize, datatype='enrichment', arraytype='upper',
                                             returnmapping=True, silent=self.silent)
        self.scores[chrom] = numpy.zeros(data.shape, dtype=numpy.float32)
        _hic_peaks.calculate_hiccups_scores(
                data,
                self.scores[chrom],
                self.minwidth,
                self.maxwidth,
                self.pixel,
                self.minobs
            )











