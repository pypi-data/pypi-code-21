# -*- coding: utf-8 -*-
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016-2017 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#      Mélissa Cardon <melissa.cardon@pasteur.fr>, 
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
"""Pacbio QC and stats"""
import collections
import json
import random

from sequana.lazy import pylab
from sequana.lazy import numpy as np
from sequana.lazy import pandas as pd
from sequana.lazy import biokit
import pysam

from sequana import logger

__all__ = ["BAMPacbio", "PBSim", "BAMSimul"]


class PacbioBAMBase(object):
    """Base class for Pacbio BAM files"""
    def __init__(self, filename):
        """

        :param str filename: input BAM file

        """
        self.filename = filename
        self.data = pysam.AlignmentFile(filename, check_sq=False)
        self._N = None
        self._df = None
        self._nb_pass = None

    def __len__(self):
        if self._N is None:
            df = self._get_df()
        return self._N

    def __str__(self):
        return "Length: {}".format(len(self))

    def reset(self):
        self.data.close()
        self.data = pysam.AlignmentFile(self.filename, check_sq=False)

    def _to_fastX(self, mode, output_filename, threads=2):
        """

        :param mode: fastq or fasta

        """
        # for now, we use samtools
        # can use bamtools as well but as long and output 10% larger (sequences
        # are split on 80-characters length)
        from snakemake import shell
        cmd = "samtools %s  -@ %s %s > %s" % (mode, threads,
            self.filename, output_filename)
        logger.info("Please be patient")
        logger.info("This may be long depending on your input data file: ")
        logger.info("typically, a minute per  500,000 reads")
        shell(cmd)
        logger.info("done")

    def to_fastq(self, output_filename, threads=2):
        """Export BAM reads into FastQ file"""
        self._to_fastX("fastq", output_filename, threads=threads)

    def to_fasta(self, output_filename, threads=2):
        """Export BAM reads into a Fasta file

        :param output_filename: name of the output file (use .fasta extension)
        :param int threads: number of threads to use

        .. note:: this executes a shell command based on samtools

        .. warning:: this takes a few minutes for 500,000 reads

        """
        self._to_fastX("fasta", output_filename, threads=threads)

    def hist_GC(self, bins=50, alpha=0.5, hold=False, fontsize=12,
                grid=True, xlabel="GC %", ylabel="#", label="",title=None):
        """Plot histogram GC content

        :param int bins: binning for the histogram
        :param float alpha: transparency of the histograms
        :param bool hold:
        :param int fontsize: fontsize of the x and y labels and title.
        :param bool grid: add grid or not
        :param str xlabel: 
        :param str ylabel:
        :param str label: label of the histogram (for the legend)
        :param str title:

        .. plot::
            :include-source:

            from sequana.pacbio import BAMPacbio
            from sequana import sequana_data
            b = BAMPacbio(sequana_data("test_pacbio_subreads.bam"))
            b.hist_GC()

        """
        if self._df is None:
            self._get_df()
        mean_GC =  np.mean(self._df.loc[:,'GC_content'])

        # set title if needed
        if title is None:
            title = "GC %%  \n Mean GC : %.2f" %(mean_GC)

        # histogram GC percent
        if hold is False:
            pylab.clf()
        pylab.hist(self._df.loc[:,'GC_content'], bins=bins,
            alpha=alpha, label=label + ", mean : " + str(round(mean_GC,2))
            + ", N : " + str(self._N))
        pylab.xlabel(xlabel, fontsize=fontsize)
        pylab.ylabel(ylabel, fontsize=fontsize)
        pylab.title(title, fontsize=fontsize)
        if grid is True:
            pylab.grid(True)
        pylab.xlim([0, 100])

    def plot_GC_read_len(self, hold=False, fontsize=12, bins=[40,40],
                grid=True, xlabel="GC %", ylabel="#"):
        """Plot GC content versus read length

        :param bool hold:
        :param int fontsize: for x and y labels and title
        :param bins: a integer or tuple of 2 integers to specify
            the binning of the x and y 2D histogram.
        :param bool grid:
        :param str xlabel:
        :param str ylabel:

        .. plot::
            :include-source:

            from sequana.pacbio import BAMPacbio
            from sequana import sequana_data
            b = BAMPacbio(sequana_data("test_pacbio_subreads.bam"))
            b.plot_GC_read_len(bins=[10, 10])

        """
        if self._df is None:
            self._get_df()
        mean_len =  np.mean(self._df.loc[:,'read_length'])
        mean_GC =  np.mean(self._df.loc[:,'GC_content'])

        if hold is False:
            pylab.clf()
        data = self._df.loc[:,['read_length','GC_content']]
        h = biokit.viz.hist2d.Hist2D(data)
        res = h.plot(bins=bins, contour=False, nnorm='log', Nlevels=6)
        pylab.xlabel("Read length", fontsize=fontsize)
        pylab.ylabel("GC %", fontsize=fontsize)
        pylab.title("GC %% vs length \n Mean length : %.2f , Mean GC : %.2f" % 
            (mean_len, mean_GC), fontsize=fontsize)
        pylab.ylim([0, 100])
        if grid is True:
            pylab.grid(True)

    def hist_len(self, bins=50, alpha=0.5, hold=False, fontsize=12,
                grid=True,xlabel="Read Length",ylabel="#", label="",
                title=None):
        """Plot histogram Read length

        :param int bins: binning for the histogram
        :param float alpha: transparency of the histograms
        :param bool hold:
        :param int fontsize:
        :param bool grid:
        :param str xlabel:
        :param str ylabel:
        :param str label: label of the histogram (for the legend)
        :param str title:

        .. plot::
            :include-source:

            from sequana.pacbio import BAMPacbio
            from sequana import sequana_data
            b = BAMPacbio(sequana_data("test_pacbio_subreads.bam"))
            b.hist_len()

        """
        if self._df is None:
            self._get_df()
        mean_len =  np.mean(self._df.loc[:,'read_length'])

        # set title if not provided
        if title is None:
            title = "Read length  \n Mean length : %.2f" %(mean_len)

        # histogram GC percent
        if hold is False:
            pylab.clf()
        pylab.hist(self._df.loc[:,'read_length'], bins=bins, alpha=alpha,
            label=  "%s, mean : %.0f, N : %d" % (label, mean_len, self._N) )
        pylab.xlabel(xlabel, fontsize=fontsize)
        pylab.ylabel(ylabel, fontsize=fontsize)
        pylab.title(title, fontsize=fontsize)
        if grid is True:
            pylab.grid(True)


class BAMPacbio(PacbioBAMBase):
    """BAM reader for Pacbio (reads)

    You can read a file as follows::

        from sequana.pacbio import BAMPacbio
        from sequana import sequana_data
        filename = sequana_data("test_pacbio_subreads.bam")
        b = BAMPacbio(filename)

    A summary of the data is stored in the attribute :attr:`df`. It contains
    information such as the length of the reads, the ACGT content, the GC content.

    Several plotting methods are available. For instance, :meth:`hist_snr`.

    """
    def __init__(self, filename):
        """.. rubric:: Constructor

        :param str filename: filename of the input pacbio BAM file. The content
            of the BAM file is not the ouput of a mapper. Instead, it is the
            output of a Pacbio (Sequel) sequencing (e.g., subreads).
        """
        super(BAMPacbio, self).__init__(filename)

    def _get_df(self):
        # When scanning the BAM, we can extract the length, SNR of ACGT (still
        # need to know how to use it). The GC content (note there is no
        # ambiguity so no S character). The ZMW. Also, from the tags we could
        # get more
        if self._df is None:
            logger.info("Scanning input file. Please wait")
            self.reset()
            N = 0

            all_results = []
            for read in self.data:
                res = []
                # count reads
                N += 1
                if (N % 10000) == 0:
                    logger.info("Read %d sequences" %N)
                #res[0] = read length
                res.append(read.query_length)
                # collections.counter is slow, let us do it ourself
                res.append( 100. / read.qlen * sum(
                    [read.query_sequence.count(letter) for letter in "CGcgSs"]))

                # res[2] = snr A
                # res[3] = snr C
                # res[4] = snr G
                # res[5] = snr T
                snr = list([x for x in read.tags if x[0]=='sn'][0][1])
                res = res + snr
                #res[6] = ZMW name
                res.append(read.qname.split('/')[1])

                # aggregate results
                all_results.append(res)

            self._df = pd.DataFrame(all_results,
                columns=['read_length','GC_content','snr_A','snr_C','snr_G','snr_T','ZMW'])
            self._N = N
            self.reset()
        return self._df
    df = property(_get_df)

    def _get_stats(self):
        # cast to allows json dump
        data =  self.df.read_length.describe().to_dict()
        data['nb_bases'] = int(self.df.read_length.sum())
        data['mean_GC'] = float(self.df.GC_content.mean())
        return data
    stats = property(_get_stats, doc="return basic stats about the read length")

    def _get_ZMW_passes(self):
        if self._nb_pass is None:
            if self._df is None:
                self._get_df()

            zmw_passes = collections.Counter(self._df.loc[:,'ZMW'])
            distrib_nb_passes = [zmw_passes[z] for z in zmw_passes.keys()]
            self._nb_pass = collections.Counter(distrib_nb_passes)
        return self._nb_pass
    nb_pass = property(_get_ZMW_passes, doc="number of passes (ZMW)")

    def stride(self, output_filename, stride=10, shift=0, random=False):
        """Write a subset of reads to BAM output

        :param str output_filename: name of output file
        :param int stride: optionnal, number of reads to read to output one read
        :param int shift: number of reads to ignore at the begining of input file
        :param bool random: if True, at each step the read to output is randomly selected
        """
        assert output_filename != self.filename, \
            "output filename should be different from the input filename"
        self.reset()
        with pysam.AlignmentFile(output_filename,"wb", template=self.data) as fh:
            if random:
                shift = np.random.randint(stride)

            for i, read in enumerate(self.data):
                if (i + shift) % stride == 0:
                    fh.write(read)
                    if random:
                        shift = np.random.randint(stride)

    def random_selection(self, output_filename, nreads=None,
            expected_coverage=None, reference_length=None):
        """Select random reads

        :param nreads: number of reads to select randomly. Must be less than
            number of available reads in the orignal file.
        :param expected_coverage:
        :param reference_length:

        of expected_coverage and reference_length provided, nreads is replaced
        automatically.
        """
        assert output_filename != self.filename, \
            "output filename should be different from the input filename"
        self.reset()

        if expected_coverage and reference_length:
            mu = self.stats['mean']
            nreads = int(expected_coverage * reference_length / mu)

        assert nreads < len(self), "nreads parameter larger than actual Number of reads"
        selector = random.sample(range(len(self)), nreads)
        logger.info("Creating a pacbio BAM file with {} reads".format(nreads))

        with pysam.AlignmentFile(output_filename,"wb", template=self.data) as fh:
            for i, read in enumerate(self.data):
                if i in selector:
                    fh.write(read)

    def summary(self):
        summary = {"name": "sequana_summary_pacbio_qc"}
        summary["read_stats"] = self.stats.copy()
        summary["mean_gc"] = float(np.mean(self._df.loc[:,'GC_content']))
        a, b = np.histogram(self._df.loc[:,'GC_content'], bins=100)
        summary['hist_gc'] = {"Y": a.tolist(), "X": b.tolist()}
        a, b =  np.histogram(self._df['read_length'],100)
        summary['hist_read_length'] = {"Y": a.tolist(), "X": b.tolist()}
        return summary

    def save_summary(self, filename):
        summary = self.summary()
        with open(filename, "w") as fh:
            json.dump(summary, fh, indent=4, sort_keys=True)

    def filter_length(self, output_filename, threshold_min=0,
        threshold_max=np.inf):
        """Select and Write reads within a given range

        :param str output_filename: name of output file
        :param int threshold_min: minimum length of the reads to keep
        :param int threshold_max: maximum length of the reads to keep

        """
        assert threshold_min < threshold_max
        assert output_filename != self.filename, \
            "output filename should be different from the input filename"
        self.reset()
        with pysam.AlignmentFile(output_filename,  "wb", template=self.data) as fh:
            for read in self.data:
                if ((read.query_length > threshold_min) & (read.query_length < threshold_max)):
                    fh.write(read)

    def hist_snr(self, bins=50, alpha=0.5, hold=False, fontsize=12,
                grid=True, xlabel="SNR", ylabel="#",title=""):
        """Plot histogram of the ACGT SNRs for all reads

        :param int bins: binning for the histogram
        :param float alpha: transparency of the histograms
        :param bool hold:
        :param int fontsize:
        :param bool grid:
        :param str xlabel:
        :param str ylabel:
        :param str title:

        .. plot::
            :include-source:

            from sequana.pacbio import BAMPacbio
            from sequana import sequana_data
            b = BAMPacbio(sequana_data("test_pacbio_subreads.bam"))
            b.hist_snr()

        """
        if self._df is None:
            self._get_df()

        if hold is False:
            pylab.clf()
        pylab.hist(self._df.loc[:,'snr_A'], alpha=alpha, label="A", bins=bins)
        pylab.hist(self._df.loc[:,'snr_C'], alpha=alpha, label="C", bins=bins)
        pylab.hist(self._df.loc[:,'snr_G'], alpha=alpha, label="G", bins=bins)
        pylab.hist(self._df.loc[:,'snr_T'], alpha=alpha, label="T", bins=bins)
        pylab.legend()
        pylab.xlabel(xlabel, fontsize=fontsize)
        pylab.ylabel(ylabel, fontsize=fontsize)
        pylab.title(title,fontsize=fontsize)
        if grid is True:
            pylab.grid(True)

    def hist_ZMW_subreads(self, alpha=0.5, hold=False, fontsize=12,
                          grid=True, xlabel="Number of ZMW passes",
                          ylabel="#", label="", title="Number of ZMW passes"):
        """Plot histogram of number of reads per ZMW (number of passes)

        :param float alpha: transparency of the histograms
        :param bool hold:
        :param int fontsize:
        :param bool grid:
        :param str xlabel:
        :param str ylabel:
        :param str label: label of the histogram (for the legend)
        :param str title:

        .. plot::
            :include-source:

            from sequana.pacbio import BAMPacbio
            from sequana import sequana_data
            b = BAMPacbio(sequana_data("test_pacbio_subreads.bam"))
            b.hist_ZMW_subreads()
        """
        if self._nb_pass is None:
            self._get_ZMW_passes()

        max_nb_pass = max(self._nb_pass.keys())
        k = range(1, max_nb_pass+1)
        val = [self._nb_pass[i] for i in k]

        # histogram nb passes
        if hold is False:
            pylab.clf()
        pylab.bar(k, val, alpha=alpha, label=label)
        if len(k) < 5:
            pylab.xticks(range(6), range(6))

        pylab.xlabel(xlabel, fontsize=fontsize)
        pylab.ylabel(ylabel, fontsize=fontsize)
        pylab.yscale('log')
        pylab.title(title, fontsize=fontsize)
        if grid is True:
            pylab.grid(True)


class BAMSimul(PacbioBAMBase):
    """BAM reader for Pacbio simulated reads (PBsim)

    A summary of the data is stored in the attribute :attr:`df`. It contains
    information such as the length of the reads, the ACGT content, the GC content.

    """
    def __init__(self, filename):
        """.. rubric:: Constructor

        :param str filename: filename of the input pacbio BAM file. The content
            of the BAM file is not the ouput of a mapper. Instead, it is the
            output of a Pacbio (Sequel) sequencing (e.g., subreads).
        """
        super(BAMSimul, self).__init__(filename)

    def _get_df(self):
        if self._df is None:
            self.reset()
            N = 0

            all_results = []
            for read in self.data:
                res = []
                # count reads
                N += 1
                if (N % 10000) == 0:
                    print("Read %d sequences" %N)
                #res[0] = read length
                res.append(read.query_length)
                # res[1] = GC content
                c = collections.Counter(read.query_sequence)
                res.append( 100 * (c['g'] + c['G'] + c['c'] + c['C']) /
                            float(sum(c.values())) )

                # aggregate results
                all_results.append(res)

            self._df = pd.DataFrame(all_results,
                columns=['read_length','GC_content'])
            self._N = N
            self.reset()
        return self._df
    df = property(_get_df)

    def filter_length(self, output_filename, threshold_min=0,
        threshold_max=np.inf):
        """Select and Write reads within a given range

        :param str output_filename: name of output file
        :param int threshold_min: minimum length of the reads to keep
        :param int threshold_max: maximum length of the reads to keep

        """
        assert threshold_min < threshold_max
        assert output_filename != self.filename, \
            "output filename should be different from the input filename"
        self.reset()
        with pysam.AlignmentFile(output_filename,  "wb", template=self.data) as fh:
            for read in self.data:
                if ((read.query_length > threshold_min) & (read.query_length < threshold_max)):
                    fh.write(read)

    def filter_bool(self, output_filename, mask):
        """Select and Write reads using a mask

        :param str output_filename: name of output file
        :param list list_bool: True to write read to output, False to ignore it

        """
        assert output_filename != self.filename, \
            "output filename should be different from the input filename"
        assert len(mask) == self._N, \
            "list of bool must be the same size as BAM file"
        self.reset()
        with pysam.AlignmentFile(output_filename,  "wb", template=self.data) as fh:
            for read, keep in zip(self.data, mask):
                if keep:
                    fh.write(read)


class PBSim(object):
    """Filter an input BAM (simulated with pbsim) so as so keep 
    reads that fit a target distribution.

    This uses a MH algorithm behind the scene.

    ::

        ss = pacbio.PBSim("test10X.bam")
        clf(); 
        ss.run(bins=100, step=50)


    """
    def __init__(self, input_bam, simul_bam):
        self.bam = BAMPacbio(input_bam)
        self.Nreads = len(self.bam)
        self.bam_simul = BAMSimul(simul_bam)

    def target_distribution(self, xprime):

        """The target distribution

        Compute histogram. Get X, Y.  Given xprime, interpolate to get yprime
        use e.g. np.interp

        """
        return np.interp(xprime, self.X[1:self.bins+1], self.Y)

    def run(self, bins=50, xmin=0, xmax=30000, step=1000, burn=1000,alpha=1,output_filename=None):
        # compute histogram of the input reads once for all to be used
        # in the target_distribution method
        self.bins = bins
        self.Y, self.X = np.histogram(self.bam.df.read_length, bins=bins, normed=True)

        lengths = self.bam_simul.df.read_length.values
        self.tokeep = []
        vec = []
        x = self.bam.df.read_length.mean()
        for i in range(self.bam_simul.df.shape[0]):
            can = lengths[i]
            aprob = min([alpha,self.target_distribution(can)/self.target_distribution(x)])
            #acceptance probability
            u = pylab.uniform(0,1)
            if u < aprob:
                x = can
                vec.append(x)
                self.tokeep.append(True)
            else:
                self.tokeep.append(False)

        #plotting the results:
        #theoretical curve
        x = pylab.arange(xmin, xmax, step)
        y = self.target_distribution(x)
        pylab.subplot(211)
        pylab.title('Metropolis-Hastings')
        pylab.plot(vec)
        pylab.subplot(212)

        pylab.hist(vec[burn:], bins=bins,normed=1)
        pylab.plot(x,y,'r-')
        pylab.ylabel('Frequency')
        pylab.xlabel('x')
        pylab.legend(('PDF','Samples'))

        if output_filename is not None:
            self.bam_simul.filter_bool(output_filename, self.tokeep)










