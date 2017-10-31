from __future__ import division, print_function
from collections import OrderedDict, Counter, defaultdict
from functools import partial
from bisect import bisect_left
from multiprocess import Pool
import itertools
import warnings
import sys
import six

import numpy as np
import pandas as pd
import h5py

from cooler.util import rlencode, get_binsize, parse_region


def check_bins(bins, chromsizes):
    is_cat = pd.api.types.is_categorical(bins['chrom'])
    bins = bins.copy()
    if not is_cat:
        bins['chrom'] = pd.Categorical(
            bins.chrom, 
            categories=list(chromsizes.index), 
            ordered=True)
    else:
        assert (bins['chrom'].cat.categories == chromsizes.index).all()

    return bins


class GenomeSegmentation(object):
    def __init__(self, chromsizes, bins):
        bins = check_bins(bins, chromsizes)
        self._bins_grouped = bins.groupby('chrom', sort=False)
        nbins_per_chrom = self._bins_grouped.size().values

        self.chromsizes = chromsizes
        self.binsize = get_binsize(bins)
        self.contigs = list(chromsizes.keys())
        self.bins = bins
        self.idmap = pd.Series(
            index=chromsizes.keys(), 
            data=range(len(chromsizes)))
        self.chrom_binoffset = np.r_[0, np.cumsum(nbins_per_chrom)]
        self.chrom_abspos = np.r_[0, np.cumsum(chromsizes.values)]
        self.start_abspos = (self.chrom_abspos[bins['chrom'].cat.codes] + 
                             bins['start'].values)
    
    def fetch(self, region):
        chrom, start, end = parse_region(region, self.chromsizes)
        result = self._bins_grouped.get_group(chrom)
        if start > 0 or end < self.chromsizes[chrom]:
            lo = result['end'].values.searchsorted(start, side='right')
            hi = lo + result['start'].values[lo:].searchsorted(end, side='left')
            result = result.iloc[lo:hi]
        return result


class TabixIterator(object):
    def __init__(self, filepath, chromsizes, bins, **kwargs):
        try:
            import pysam
        except ImportError:
            raise ImportError("pysam is required to read tabix-indexed files")

        # all requested contigs will be placed in the output matrix
        self.gs = GenomeSegmentation(chromsizes, bins)
        
        # find available contigs in the contact list
        self.filepath = filepath
        self.C2 = kwargs.pop('C2', 3)
        self.P2 = kwargs.pop('P2', 4)
        with pysam.TabixFile(filepath, 'r', encoding='ascii') as f:
            try:
                self.file_contigs = [c.decode('ascii') for c in f.contigs]
            except AttributeError:
                self.file_contigs = f.contigs
        warnings.warn(
            "NOTE: When using the Tabix aggregator, make sure the order of "
            "chromosomes in the provided chromsizes agrees with the chromosome "
            "ordering of read ends in the contact list file.")

    def init(self):
        import pysam
        self.f = pysam.TabixFile(self.filepath, 'r', encoding='ascii')
        self.parser = pysam.asTuple()

    def iter_contacts(self, chrom1, start, end):
        f = self.f
        C2 = self.C2
        P2 = self.P2
        idmap = self.gs.idmap
        for line in f.fetch(chrom1, start, end, parser=self.parser):
            chrom2 = line[C2]
            pos2 = int(line[P2])
            try:
                cid2 = idmap[chrom2]
            except KeyError:
                # this chrom2 is not requested
                continue
            yield cid2, pos2


class PairixIterator(object):
    def __init__(self, filepath, chromsizes, bins):
        try:
            import pypairix
        except ImportError:
            raise ImportError(
                "pypairix is required to read pairix-indexed files")
        
        # all requested contigs will be placed in the output matrix
        self.gs = GenomeSegmentation(chromsizes, bins)

        # find available contigs in the contact list
        self.filepath = filepath
        f = pypairix.open(filepath, 'r')
        self.C1 = f.get_chr1_col()
        self.C2 = f.get_chr2_col()
        self.P1 = f.get_startpos1_col()
        self.P2 = f.get_startpos2_col()
        self.file_contigs = set(
            itertools.chain.from_iterable(
                [b.split('|') for b in f.get_blocknames()]))
        del f

    def init(self):
        import pypairix
        self.f = pypairix.open(self.filepath, 'r')
    
    def iter_contacts(self, chrom1, start, end):
        #f = FILE #self.f #pypairix.open(self.filepath, 'r')
        f = self.f
        P1 = self.P1
        P2 = self.P2
        chromsizes = self.gs.chromsizes
        remaining_chroms = self.gs.idmap[chrom1:]
        for chrom2, cid2 in six.iteritems(remaining_chroms):
            
            chrom2_size = chromsizes[chrom2]

            if chrom1 != chrom2 and f.exists2(chrom2, chrom1):  # flipped
                iterator = f.query2D(chrom2, 0, chrom2_size, 
                                     chrom1, start, end)
                pos2_col = P1
            else:
                iterator = f.query2D(chrom1, start, end, 
                                     chrom2, 0, chrom2_size)
                pos2_col = P2

            for line in iterator:
                pos2 = int(line[pos2_col])
                yield cid2, pos2


def aggregate_one(iterator, bin1):
    binsize = iterator.gs.binsize
    chrom_binoffset = iterator.gs.chrom_binoffset
    chrom_abspos = iterator.gs.chrom_abspos
    start_abspos = iterator.gs.start_abspos
    
    bin1_id, chrom1, start, end = bin1
    print(chrom1, start, end, flush=True)

    accumulator = Counter()
    for cid2, pos2 in iterator.iter_contacts(chrom1, start, end):
        if binsize is None:
            lo = chrom_binoffset[cid2]
            hi = chrom_binoffset[cid2 + 1]
            bin2_id = lo + np.searchsorted(
                start_abspos[lo:hi], 
                chrom_abspos[cid2] + pos2,
                side='right') - 1
        else:
            bin2_id = chrom_binoffset[cid2] + (pos2 // binsize)
        accumulator[bin2_id] += 1

    if len(accumulator):
        bin2_ids = np.array(list(accumulator.keys()))
        counts = np.array(list(accumulator.values()))
        idx = np.argsort(bin2_ids)
        return {
            'bin1_id': bin1_id,
            'bin2_id': bin2_ids[idx],
            'count':   counts[idx],
        }


def aggregate_many(iterator, bin1s):
    binsize = iterator.gs.binsize
    chrom_binoffset = iterator.gs.chrom_binoffset
    chrom_abspos = iterator.gs.chrom_abspos
    start_abspos = iterator.gs.start_abspos
    accumulator = Counter()
    binned = defaultdict(list)

    print(bin1s[-1], flush=True)

    for bin1_id, chrom1, start, end in bin1s:

        for cid2, pos2 in iterator.iter_contacts(chrom1, start, end):
            if binsize is None:
                lo = chrom_binoffset[cid2]
                hi = chrom_binoffset[cid2 + 1]
                bin2_id = lo + np.searchsorted(
                    start_abspos[lo:hi], 
                    chrom_abspos[cid2] + pos2,
                    side='right') - 1
            else:
                bin2_id = chrom_binoffset[cid2] + (pos2 // binsize)
            accumulator[bin2_id] += 1

        if len(accumulator):
            bin2_ids = np.array(list(accumulator.keys()))
            counts = np.array(list(accumulator.values()))
            idx = np.argsort(bin2_ids)
            binned['bin1_id'].extend([bin1_id] * len(idx))
            binned['bin2_id'].extend(bin2_ids[idx])
            binned['count'].extend(counts[idx])
            accumulator.clear()

    return binned if len(binned) else None


contact_iterator = None
class Worker(object):
    @staticmethod
    def init(iterator):
        global contact_iterator
        contact_iterator = iterator
        contact_iterator.init()

    @staticmethod
    def job(bin1):
        global contact_iterator
        return aggregate_one(contact_iterator, bin1)


    @staticmethod
    def job2(bin1s):
        global contact_iterator
        return aggregate_many(contact_iterator, bin1s)



def aggregate(iterator, bins, nproc):
    import dill
    import pickle
    dill.settings['protocol'] = pickle.HIGHEST_PROTOCOL

    # warn about requested contigs not seen in the contact list
    for chrom in iterator.gs.contigs:
        if chrom not in iterator.file_contigs:
            warnings.warn(
                "Did not find contig " +
                " '{}' in contact list file.".format(chrom))

    #job = partial(aggregate_worker, iterator)
    bin_tuples = bins.to_records()

    chunksize = 500
    edges = np.arange(0, len(bin_tuples)+chunksize, chunksize)
    bin_tuples_split = [
        bin_tuples[lo:hi] 
            for lo, hi in zip(edges[:-1], edges[1:])
    ]

    try:
        if nproc > 1:
            pool = Pool(nproc, initializer=Worker.init, initargs=[iterator])
            #logger.info("Using {} cores".format(nproc))
            map = pool.imap
        else:
            map = six.moves.map
        for chunk in map(Worker.job2, bin_tuples_split):
            if chunk is None:
                continue
            yield pd.DataFrame(
                chunk, 
                columns=['bin1_id', 'bin2_id', 'count'])
    finally:
        if nproc > 1:
            pool.close()


def aggregate_cooler(input_uri, output_uri, factor, nproc, chunksize, lock):
    c = api.Cooler(input_uri)
    chromsizes = c.chromsizes
    new_binsize = c.binsize * factor
    new_bins = binnify(chromsizes, new_binsize)

    try:
        # Note: fork before opening to prevent inconsistent global HDF5 state
        if nproc > 1:
            pool = mp.Pool(nproc)

        iterator = CoolerAggregator(
            input_uri,
            new_bins,
            chunksize,
            batchsize=nproc,
            map=pool.map if nproc > 1 else map)

        create(
            output_uri,
            new_bins,
            iterator,
            lock=lock,
            append=True)

    finally:
        if nproc > 1:
            pool.close()


def get_multiplier_sequence(resolutions, bases=None):
    """
    From a set of target resolutions and one or more base resolutions
    deduce the most efficient sequence of integer multiple aggregations
    to satisfy all targets starting from the base resolution(s).
    
    Parameters
    ----------
    resolutions: sequence of int
        The target resolutions
    bases: sequence of int, optional
        The base resolutions for which data already exists.
        If not provided, the smallest resolution is assumed to be the base.
    
    Returns
    -------
    resn: 1D array
        Resolutions, sorted in ascending order.
    pred: 1D array
        Index of the predecessor resolution in `resn`. A value of -1 implies
        that the resolution is a base resolution.
    mult: 1D array
        Multiplier to go from predecessor to target resolution.
    
    """
    if bases is None:
        # assume the base resolution is the smallest one
        bases = {min(resolutions)}
    else:
        bases = set(bases)

    resn = np.array(sorted(bases.union(resolutions)))
    pred = -np.ones(len(resn), dtype=int)
    mult = -np.ones(len(resn), dtype=int)
  
    for i, target in list(enumerate(resn))[::-1]:
        p = i - 1
        while p >= 0:
            if target % resn[p] == 0:
                pred[i] = p
                mult[i] = target // resn[p]
                break
            else:
                p -= 1
    
    for i, p in enumerate(pred):
        if p == -1 and resn[i] not in bases:
            raise ValueError(
                "Resolution {} cannot be derived from "
                "the base resolutions: {}.".format(resn[i], bases))
            
    return resn, pred, mult


def new_multires_aggregate(input_uris, outfile, resolutions, nproc, chunksize, 
                           lock=None):
    uris = {}
    bases = set()
    for input_uri in input_uris:
        infile, ingroup = parse_cooler_uri(input_uri)
        base_binsize = api.Cooler(infile, ingroup).binsize
        uris[base_binsize] = (infile, ingroup)
        bases.add(base_binsize)

    resn, pred, mult = get_multiplier_sequence(resolutions, bases)
    n_zooms = len(resn)

    logger.info(
        "Copying base matrices and producing {} new zoom levels.".format(n_zooms)
    )
    
    # Copy base matrix
    for base_binsize in bases:
        logger.info("Bin size: " + str(base_binsize))
        infile, ingroup = uris[base_binsize]
        with h5py.File(infile, 'r') as src, \
            h5py.File(outfile, 'w') as dest:
            src.copy(ingroup, dest, '/resolutions/{}'.format(base_binsize))

    # Aggregate
    # Use lock to sync read/write ops on same file
    for i in range(n_zooms):
        if pred[i] == -1:
            continue
        prev_binsize = resn[pred[i]]
        binsize = prev_binsize * mult[i]
        logger.info(
            "Aggregating from {} to {}.".format(prev_binsize, binsize))
        aggregate(
            outfile + '::resolutions/{}'.format(prev_binsize), 
            outfile + '::resolutions/{}'.format(binsize),
            mult[i], 
            nproc, 
            chunksize,
            lock
        )

    with h5py.File(outfile, 'r+') as fw:
        fw.attrs.update({
            'format': u'HDF5::MCOOL',
            'format-version': 2,
        })

