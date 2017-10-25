# -*- coding: utf-8 -*-
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#      Dimitri Desvillechabrol <dimitri.desvillechabrol@pasteur.fr>,
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
"""Tools to manipulate BAM/SAM files

.. autosummary::

    Alignment
    BAM
    SAMFlags

.. note:: BAM being the compressed version of SAM files, we do not
    implement any functionalities related to SAM files. We strongly encourage
    developers to convert their SAM to BAM.

"""
import os
import json
from collections import Counter
from collections import OrderedDict

from sequana.lazy import pandas as pd
from sequana.lazy import numpy as np
from sequana.lazy import pylab

import pysam
from sequana import jsontool, logger

"""
#http://www.acgt.me/blog/2014/12/16/understanding-mapq-scores-in-sam-files-does-37-42#
#http://biofinysics.blogspot.fr/2014/05/how-does-bowtie2-assign-mapq-scores.html
#https://gitlab.univ-nantes.fr/a-slide/ContaVect/blob/9a411abfa720064c205c5f6c811afdfea206ed12/pyDNA/pySamTools/Bam.py

Interesting commands::

    samtools flagstat contaminant.bam
    samtools stats contaminant.bam
"""

__all__ = ['BAM','Alignment', 'SAMFlags']

# simple decorator to rewind the BAM file
from functools import wraps
def seek(f):
    @wraps(f)
    def wrapper(*args, **kargs):
        #args[0] is the self of the method
        # For BAM files only
        args[0].reset()
        return f(*args, **kargs)
    return wrapper


class BAM(pysam.AlignmentFile):
    """BAM data structure, statistics and plotting

    .. note:: Python2.7 and 3.5 behave differently
        and we would recommend the Python 3.5 version. For instance,
        :meth:`to_fastq` would work only with Python 3.5.

    We provide a test file in Sequana:

    .. doctest::

        >>> from sequana import BAM, sequana_data
        >>> b = BAM(sequana_data("test.bam"))
        >>> len(b)
        1000

    .. note:: Once you loop over this data structure,  you must call
        :meth:`reset` to force the next iterator to start at position 0 again.
        The methods implemented in this data structure take care of that
        for you thanks to a decorator called seek.
        If you want to use the :meth:`next` function, call :meth:`reset` to make sure you
        start at the beginning.




    """
    def __init__(self, filename,  mode='rb',  *args):
        """.. rubric:: Constructor

        """
        # The mode rb means read-only (r) and that the format is BAM or SAM (b)

        # super()  works for py27 but not py35 probably a missing __init__  or __new__ in
        # AlignmentFile class. See e.g., stackoverflow/questions/
        # 26653401/typeerror-object-takes-no-parameters-but-only-in-python-3

        pysam.AlignmentFile.__init__(filename, mode=mode, *args)

        self._filename = filename
        self.metrics_count = None
        # the BAM format can be rewinded but not SAM. This is a pain since one
        # need to reload the instance after each operation. With the BAM, we can
        # do that automatically. We therefore enforce the BAM format.

        # Another issue is that in PY3, there is an attribute **format** that
        # tells us if the input is BAM or SAM but this does not work in PY2
        # where the attribute is missing...

        # another know issue is that we cannot use the method is_bam trustfully.
        # Using AlignmentFile one must provide the proper mode 'e.g. rb will set
        # is_bam to True while 'r' only will set it to False. However, it seems
        # there is not sanity check inside the file. Besides, using
        # AlignmentFile.__init__ instead of the class itself seems to haev also
        # some side effects.

        # Let us save the length (handy and use in other places).
        # If it is a SAM file, the rewind does not work and calling it again wil
        # return 0. This may give us a hint that it is a SAM file
        self.N = None

        # Figure out if the data is paired-end or not
        # I believe that checking just one alignement is enough.
        self.reset()
        self.is_paired = next(self).is_paired
        self.reset()

        # running a second time the len() should return the correct answer with
        # BAM files but the SAM will not work and return 0. This takes time 
        # so let us not do it anymore in the constructor
        # if len(self) == 0:
        #     raise ValueError("Convert your SAM file to a BAM file please")

    @seek
    def get_read_names(self):
        """Return the reads' names"""
        names = [this.qname for this in self]
        return names

    @seek
    def iter_unmapped_reads(self):
        """Return an iterator on the reads that are unmapped"""
        unmapped = (this.qname for this in self if this.is_unmapped)
        return unmapped

    @seek
    def iter_mapped_reads(self):
        """Return an iterator on the reads that are mapped"""
        mapped = (this.qname for this in self if this.is_unmapped is False)
        return mapped

    @seek 
    def _get_is_sorted(self):
        pos = next(self).pos
        for this in self:
            if this.pos > pos:
                return False
        return True
    is_sorted = property(_get_is_sorted, doc="return True is the BAM is sorted")

    @seek
    def __len__(self):
        if self.N is None:
            logger.warning("Scanning the BAM. Please wait")
            self.N = sum(1 for _ in self)
            self.reset()
        return self.N

    @seek
    def get_flags(self):
        """Return flags of all reads as a list

        .. seealso:: :meth:`get_flags_as_df`, :class:`SAMFlags`"""
        flags = [s.flag for s in self]
        return flags

    def get_stats(self):
        """Return basic stats about the reads

        :return: dictionary with basic stats:

            - total_reads : number reads
            - mapped_reads : number of mapped reads
            - unmapped_reads : number of unmapped
            - mapped_proper_pair : R1 and R2 mapped face to face
            - hard_clipped_reads: number of reads with supplementary alignment
            - reads_duplicated: number of reads duplicated

        .. warning:: works only for BAM files. Use :meth:`get_full_stats_as_df`
            for SAM files.

        """

        """#See samtools stats
        # 1526795 + 0 in total (QC-passed reads + QC-failed reads)
        13 + 0 secondary
        0 + 0 supplementary
        0 + 0 duplicates
        3010 + 0 mapped (0.20% : N/A)
        1526782 + 0 paired in sequencing
        763391 + 0 read1
        763391 + 0 read2
        2700 + 0 properly paired (0.18% : N/A)
        2976 + 0 with itself and mate mapped
        21 + 0 singletons (0.00% : N/A)
        0 + 0 with mate mapped to a different chr
        0 + 0 with mate mapped to a different chr (mapQ>=5)
        """
        d = {}

        samflags_count = self.get_samflags_count()

        # all reads - (supplementary alignmnt + secondary alignmnt)
        d['total_reads'] = len(self) - (samflags_count[256] +
                                        samflags_count[2048])
        # all reads - (unmapped + supplementary alignmnt + secondary alignmnt)
        d['mapped_reads'] = d['total_reads'] - samflags_count[4]
        d['unmapped_reads'] = samflags_count[4]
        d['mapped_proper_pair'] = samflags_count[2]
        d['reads_duplicated'] = samflags_count[1024]
        return d

    def get_full_stats_as_df(self):
        """Return a dictionary with full stats about the BAM file

        The index of the dataframe contains the flags. The column contains
        the counts.

        ::

            >>> from sequana import BAM, sequana_data
            >>> b = BAM(sequana_data("test.bam"))
            >>> df = b.get_full_stats_as_df()
            >>> df.query("description=='average quality'")
            36.9

        .. note:: uses samtools behind the scene
        """
        from easydev import shellcmd
        res = shellcmd("samtools stats %s" % self._filename)
        res = res.decode('utf-8')

        # First, we can extract all data that statrts with SN
        # The format is
        #
        # SN name: value #comment
        #
        # separators are \t tabulation
        #
        # so we split with the : character, remove the starting SN\t characters
        # remove comments and ignore other \t characters. We should end up with
        # only 2 columns; names/values

        # extra all relevnt lines starting with SN
        data = [x for x in res.split("\n") if x.startswith('SN')]
        # remove comments
        data = [x.split('#')[0][3:] for x in data]
        names = [x.split(":")[0] for x in data]
        values = [x.split(":")[1].strip() for x in data]
        df = pd.DataFrame({"description": names, "count": values })
        df = df[['description', 'count']]
        df.sort_values(by='count', inplace=True)
        return df

    def get_flags_as_df(self):
        """Returns flags as a dataframe

        .. doctest::

            >>> from sequana import BAM, sequana_data
            >>> b = BAM(sequana_data('test.bam'))
            >>> df = b.get_flags_as_df()
            >>> df.sum()
            1       1000
            2        484
            4          2
            8          2
            16       499
            32       500
            64       477
            128      523
            256       64
            512        0
            1024       0
            2048       0
            dtype: int64

        .. seealso:: :class:`SAMFlags` for meaning of each flag
        """
        flags = self.get_flags()
        data = [(this, [flag&this for flag in flags])
            for this in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]]
        df = pd.DataFrame(dict(data))
        df = df > 0
        return df

    def plot_bar_flags(self, logy=True, fontsize=16, filename=None):
        """Plot an histogram of the flags contained in the BAM

        .. plot::
            :include-source:

            from sequana import BAM, sequana_data
            b = BAM(sequana_data('test.bam', "testing"))
            b.plot_bar_flags()

        .. seealso:: :class:`SAMFlags` for meaning of each flag
        """
        df = self.get_flags_as_df()
        df = df.sum()
        pylab.clf()
        if logy is True:
            barplot = df.plot(kind='bar', logy=logy, grid=True)
        else:
            barplot = df.plot(kind='bar', grid=True)
        pylab.xlabel("flags", fontsize=fontsize)
        pylab.ylabel("count", fontsize=fontsize)
        pylab.tight_layout()
        if filename:
            pylab.savefig(filename)
        return barplot

    @seek
    def to_fastq(self, filename):
        """Export the BAM to FastQ format

        .. warning:: to be tested
        .. todo:: comments from original reads ?


        Method 1 (bedtools)::

            bedtools bamtofastq -i JB409847.bam  -fq test1.fastq

        Method2 (samtools)::

            samtools bam2fq JB409847.bam > test2.fastq

        Method3 (sequana)::

            from sequana import BAM
            BAM(filename)
            BAM.to_fastq("test3.fastq")

        Note that the samtools method removes duplicated reads so the output is
        not identical to method 1 or 3.

        """
        with open(filename, "w") as fh:
            for i, this in enumerate(self):
                # FIXME what about comments
                read = this.qname
                read += this.seq + "\n"
                read += "+\n"
                read += this.qual + "\n"
                #if i != self.N-1:
                #    read += "\n"
                fh.write(read)

    @seek
    def get_mapq_as_df(self):
        """Return dataframe with mapq for each read"""
        df = pd.DataFrame({'mapq': [this.mapq for this in self]})
        return df

    @seek
    def get_mapped_read_length(self):
        """Return dataframe with read length for each read


        .. plot::

            from pylab import hist
            from sequana import sequana_data, BAM
            b = BAM(sequana_data("test.bam"))
            hist(b.get_mapped_read_length())

        """
        read_length = [read.reference_length for read in self
                       if read.is_unmapped is False]
        return read_length

    @seek
    def get_metrics_count(self):
        """ Count flags/mapq/read length in one pass."""
        mapq_dict = {}
        read_length_dict = {}
        flag_dict = {}
        mean_qualities = []
        for read in self:
            self._count_item(mapq_dict, read.mapq)
            self._count_item(flag_dict, read.flag)
            if read.is_unmapped is False:
                self._count_item(read_length_dict, read.reference_length)
            mean_qualities.append(pylab.mean(read.query_qualities))
        self.metrics_count = {"mapq": mapq_dict,
                              "read_length": read_length_dict,
                              "flags": flag_dict,
                                "mean_quality": pylab.mean(mean_qualities)}
        return self.metrics_count

    def get_samflags_count(self):
        """ Count how many reads have each flag of sam format after count
        metrics.
        """
        if self.metrics_count is None:
            self.get_metrics_count()

        samflags = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048)
        samflags_count = dict.fromkeys(samflags, 0)
        for flag, count in self.metrics_count["flags"].items():
            for samflag in samflags:
                if flag&samflag != 0:
                    self._count_item(samflags_count, samflag, count)
        return samflags_count

    def _count_item(self, d, item, n=1):
        if item in d.keys():
            d[item] += n
        else:
            d[item] = n

    def _get_read_length(self):
        if self.metrics_count is None:
            self.get_metrics_count()

        X = sorted(self.metrics_count['read_length'].keys())
        Y = [self.metrics_count['read_length'][k] for k in X]
        return X, Y

    def plot_read_length(self):
        """Plot occurences of aligned read lengths

        .. plot::
            :include-source:

            from sequana import sequana_data, BAM
            b = BAM(sequana_data("test.bam"))
            b.plot_read_length()

        """
        X, Y = self._get_read_length()
        pylab.plot(X, Y,
            label="min length:{}; max length:{}".format(min(X), max(X)))
        pylab.grid()
        pylab.xlabel("Read length", fontsize=16)
        pylab.legend()

    def plot_bar_mapq(self, fontsize=16, filename=None):
        """Plots bar plots of the MAPQ (quality) of alignments

            .. plot::
                :include-source:

                from sequana import BAM, sequana_data
                b = BAM(sequana_data('test.bam', "testing"))
                b.plot_bar_mapq()

        """
        df = self.get_mapq_as_df()
        df.plot(kind='hist', bins=range(0,df.max().values[0]+1), legend=False,
            grid=True, logy=True)
        pylab.xlabel("MAPQ", fontsize=fontsize)
        pylab.ylabel("Count", fontsize=fontsize)
        try:
            # This may raise issue on MAC platforms
            pylab.tight_layout()
        except:
            pass
        if filename:
            pylab.savefig(filename)

    def bam_analysis_to_json(self, filename):
        """ Create a json file with information related to the bam file.

        This includes some metrics (see :meth:`get_stats`; eg MAPQ),
        combination of flags, SAM flags, counters about the read length.
        """
        if self.metrics_count is None:
            self.get_metrics_count()

        d = {}
        d["module"] = "bam_analysis"
        d["metrics"] = self.get_stats()
        d["combo_flag"] = self.metrics_count["flags"]
        d["samflags"] = self.get_samflags_count()
        d["read_length"] = self.metrics_count["read_length"]
        with open(filename, "w") as fp:
            json.dump(d, fp, indent=True, sort_keys=True)

    @seek
    def get_gc_content(self):
        """Return GC content for all reads (mapped or not)

        .. seealso:: :meth:`plot_gc_content`

        """
        data = [(f.seq.count("C") + f.seq.count('G')) / len(f.seq)*100. for f in self]
        return data

    @seek
    def get_length_count(self):
        """Return counter of all fragment lengths"""
        import collections
        data = [this.rlen for this in self]
        return collections.Counter(data)

    def plot_gc_content(self, fontsize=16, ec="k", bins=100):
        """plot GC content histogram

        :params bins: a value for the number of bins or an array (with a copy()
            method)
        :param ec: add black contour on the bars

        .. plot::
            :include-source:

            from sequana import BAM, sequana_data
            b = BAM(sequana_data('test.bam'))
            b.plot_gc_content()

        """
        data = self.get_gc_content()
        try:
            X = np.linspace(0, 100, bins)
        except:
            X = bins.copy()

        pylab.hist(data, X, normed=True, ec=ec)
        pylab.grid(True)
        mu = pylab.mean(data)
        sigma = pylab.std(data)

        X = pylab.linspace(X.min(), X.max(), 100)
        pylab.plot(X, pylab.normpdf(X, mu, sigma), lw=2, color="r", ls="--")
        pylab.xlabel("GC content", fontsize=16)

    def _get_qualities(self, max_sample=500000):
        qualities = []
        for i, record in enumerate(self):
            if i < max_sample:
                #quality = [ord(x) -33 for x in record.qual]
                quality = record.query_qualities
                qualities.append(quality)
            else:
                break
        return qualities

    @seek
    def boxplot_qualities(self, max_sample=500000):
        """Same as in :class:`sequana.fastq.FastQC`

        """
        qualities = self._get_qualities(max_sample)
        df = pd.DataFrame(qualities)
        from biokit.viz.boxplot import Boxplot
        bx = Boxplot(df)
        try:
            # new version of biokit
            bx.plot(ax=ax)
        except:
            bx.plot()

    @seek
    def get_actg_content(self, max_sample=500000):
        try: self.alignments
        except: self._set_alignments()
        # what is the longest string ?
        max_length = max((len(a.seq) for a in self.alignments))
        import re
        df = pd.DataFrame(np.zeros((max_length,5)), columns=['A', 'C', 'G', 'T', 'N'])
        A = np.zeros(max_length)
        C = np.zeros(max_length)
        G = np.zeros(max_length)
        T = np.zeros(max_length)
        N = np.zeros(max_length)

        for a in self.alignments:
            pos = [m.start() for m in re.finditer("A", a.seq)]
            A[pos] += 1
            C[[m.start() for m in re.finditer("C", a.seq)]] += 1
            G[[m.start() for m in re.finditer("G", a.seq)]] += 1
            T[[m.start() for m in re.finditer("T", a.seq)]] += 1
            N[[m.start() for m in re.finditer("N", a.seq)]] += 1

        df["A"] = A
        df["C"] = C
        df["T"] = T
        df["G"] = G
        df["N"] = N

        df = df.divide(df.sum(axis=1), axis=0)

        return df

    def plot_acgt_content(self, stacked=False, fontsize=16, include_N=True):
        """Plot ACGT content

        .. plot::
            :include-source:

            from sequana import sequana_data, BAM
            b = BAM(sequana_data("measles.fa.sorted.bam"))
            b.plot_acgt_content()
        """
        df = self.get_actg_content()
        if include_N is False and "N" in df.columns:
            df.drop("N", axis=1, inplace=True)
        if stacked is True:
            df.plot.bar(stacked=True)
        else:
            df.plot()
        pylab.grid(True)
        pylab.xlabel("position (bp)", fontsize=fontsize)
        pylab.ylabel("percent", fontsize=fontsize)

    def _set_alignments(self):
        # this scans the alignments once for all
        self.alignments = [this for this in self]

    @seek
    def set_fast_stats(self):
        try: self.alignments
        except: self._set_alignments()

        reference_start = [this.reference_start for this in self.alignments]
        reference_end = [this.reference_end for this in self.alignments]
        N = max([this for this in reference_end if this])

        self.coverage = np.zeros(N)
        for x, y in zip(reference_start, reference_end):
            if y and x>=0 and y>=0: self.coverage[x:y] += 1
            else: pass

        self.insertions = []
        self.deletions = []
        for this in self.alignments:
            if this.cigarstring:
                if "I" in this.cigarstring:
                    self.insertions.extend([x[1] for x in this.cigartuples if x[0] == 1])
                if "D" in this.cigarstring:
                    self.deletions.extend([x[1] for x in this.cigartuples if x[0] == 2])

    def plot_coverage(self):
        """Please use :class:`GenomeCov` for more sophisticated
        tools to plot the genome coverage

        .. plot::
            :include-source:

            from sequana import sequana_data, BAM
            b = BAM(sequana_data("measles.fa.sorted.bam"))
            b.plot_coverage()

        """
        try: self.coverage
        except: self.set_fast_stats()
        pylab.plot(self.coverage)
        pylab.xlabel("Coverage")

    def hist_coverage(self, bins=100):
        """

        .. plot::
            :include-source:

            from sequana import sequana_data, BAM
            b = BAM(sequana_data("measles.fa.sorted.bam"))
            b.hist_coverage()
        """
        try: self.coverage
        except: self.set_fast_stats()
        pylab.hist(self.coverage, bins=bins)
        pylab.xlabel("Coverage")
        pylab.ylabel("Number of mapped bases")
        pylab.grid()


    @seek
    def plot_indel_dist(self, fontsize=16):
        """Plot indel count (+ ratio)

        :Return: list of insertions, deletions and ratio insertion/deletion for
            different length starting at 1  

        .. plot::
            :include-source:

            from sequana import sequana_data, BAM
            b = BAM(sequana_data("measles.fa.sorted.bam"))
            b.plot_indel_dist()

        What you see on this figure is the presence of 10 insertions of length
        1, 1 insertion of length 2 and 3 deletions of length 1


        # Note that in samtools, several insertions or deletions in a single
        alignment are ignored and only the first one seems to be reported. For
        instance 10M1I10M1I stored only 1 insertion in its report; Same comment
        for deletions.
        """
        try:
            self.insertions
        except:
            self.set_fast_stats()
        if len(self.insertions) ==0 or len(self.deletions) == 0:
            raise ValueError("No deletions or insertions found")

        N = max(max(Counter(self.deletions)), max(Counter(self.insertions))) + 1
        D = [self.deletions.count(i) for i in range(N)]
        I = [self.insertions.count(i) for i in range(N)]
        R = [i/d if d!=0 else 0 for i,d in zip(I, D)]
        fig, ax = pylab.subplots()
        ax.plot(range(N), I, marker="x", label="Insertions")
        ax.plot(range(N), D, marker="x", label="Deletions")
        ax.plot(range(N), R, "--r", label="Ratio insertions/deletions")
        ax.set_yscale("symlog")
        pylab.ylim([1, pylab.ylim()[1]])
        pylab.legend()
        pylab.grid()
        from matplotlib.ticker import MaxNLocator
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        pylab.xlabel("Indel length", fontsize=fontsize)
        pylab.ylabel("Indel count", fontsize=fontsize)
        return I, D, R


class Alignment(object):
    """Helper class to retrieve info about Alignment

    Takes an alignment as read by :class:`BAM` and provides a simplified version
    of pysam.Alignment class.

    ::

        >>> from sequana.bamtools import Alignment
        >>> from sequana import BAM, sequana_data
        >>> b = BAM(sequana_data("test.bam"))
        >>> segment = next(b)
        >>> align = Alignment(segment)
        >>> align.as_dict()
        >>> align.FLAG
        353

    The original data is stored in hidden attribute :attr:`_data` and the
    following values are available as attributes or dictionary:


    * QNAME: a query template name. Reads/segment having same QNAME come from the
      same template. A QNAME set to `*` indicates the information is unavailable.
      In a sam file, a read may occupy multiple alignment
    * FLAG: combination of bitwise flags. See :class:`SAMFlags`
    * RNAME: reference sequence
    * POS
    * MAPQ: mapping quality if segment is mapped. equals -10 log10 Pr
    * CIGAR: See :class:`sequana.cigar.Cigar`
    * RNEXT: reference sequence name of the primary alignment of the NEXT read
      in the template
    * PNEXT: position of primary alignment
    * TLEN: signed observed template length
    * SEQ: segment sequence
    * QUAL: ascii of base quality


    """
    def __init__(self, alignment):
        """.. rubric:: constructor

        :param alignment: alignment instance from :class:`BAM`


        """
        self._data = alignment
        d = self.as_dict()
        for key in d.keys():
            setattr(self, key, d[key])

    def as_dict(self):
        d = {}
        s = self._data
        d['QNAME'] = s.qname
        d['FLAG'] = s.flag
        d['RNAME'] = s.rname
        d['POS'] = s.pos
        d['MAPQ'] = s.mapq
        d['CIGAR'] = s.cigar
        d['PNEXT'] = s.pnext
        d['RNEXT'] = s.rnext
        d['TLEN'] = s.tlen
        d['SEQ'] = s.seq
        d['QUAL'] = s.qual
        return d


class SAMFlags(object):
    """Utility to extract bits from a SAM flag

    .. doctest::

        >>> from sequana import SAMFlags
        >>> sf = SAMFlags(257)
        >>> sf.get_flags()
        [1, 256]


    You can also print the bits and their description::

        print(sf)

    ======= ====================================================================
    bit     Meaning/description
    ======= ====================================================================
    1       template having multiple segments in sequencing
    2       each segment properly aligned according to the aligner
    4       segment unmapped
    8       next segment in the template unmapped
    16      SEQ being reverse complemented
    32      SEQ of the next segment in the template being reverse complemented
    64      the first segment in the template
    128     the last segment in the template
    256     secondary alignment
    512     not passing filters, such as platform/vendor quality controls
    1024    PCR or optical duplicate
    2048    supplementary alignment
    ======= ====================================================================

    :reference: http://samtools.github.io/hts-specs/SAMv1.pdf
    """
    def __init__(self, value=4095):
        self.value = value
        self._flags = {
            1: "template having multiple segments in sequencing",
            2: "each segment properly aligned according to the aligner",
            4: "segment unmapped",
            8: "next segment in the template unmapped",
            16: "SEQ being reverse complemented",
            32: "SEQ of the next segment in the template being reverse complemented",
            64: "the first segment in the template",
            128: "the last segment in the template",
            256: "secondary alignment",
            512: "not passing filters, such as platform/vendor quality controls",
            1024: "PCR or optical duplicate",
            2048: "supplementary alignment"}

    def get_meaning(self):
        """Return all description sorted by bit """
        return [self._flags[k] for k in sorted(self._flags.keys())]

    def get_flags(self):
        """Return the individual bits included in the flag"""
        flags = []
        for this in sorted(self._flags.keys()):
            if self.value & this:
                flags.append(this)
        return flags

    def __str__(self):
        txt = ""
        for this in sorted(self._flags.keys()):
            if self.value & this:
                txt += "%s: %s\n" % (this, self._flags[this])
        return txt
