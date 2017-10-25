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
""".. rubric:: Standalone application dedicated to coverage"""
import os
import shutil
import glob
import sys
import argparse
from optparse import OptionParser
from argparse import RawTextHelpFormatter

from sequana import bedtools
from sequana.modules_report.coverage import CoverageModule
from sequana.modules_report.coverage import ChromosomeCoverageModule 
from sequana.utils import config
from sequana import logger
from sequana import sequana_debug_level
from sequana.bedtools import GenomeCov, FilteredGenomeCov

from easydev import shellcmd, mkdirs
from easydev.console import purple

from pylab import show, figure, savefig


# http://stackoverflow.com/questions/18462610/argumentparser-epilog-and-description-formatting-in-conjunction-with-argumentdef
class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


class Options(argparse.ArgumentParser):
    def  __init__(self, prog="sequana_coverage"):
        usage = purple("""\nWelcome to SEQUANA -- Coverage standalone

    Extract and plot coverage of one or more chromosomes/contigs in a BED or BAM
    file. In addition, running median used in conjunction with double thresholds
    extract regions of interests (low or high coverage). A reference may be
    provided to plot the coverage versus GC content. 

    The input file should be one of the following:

    - a BED file that is a tabulated file at least 3 columns.
      The first column being the reference, the second is the position 
      and the third column contains the coverage itself. 
    - or a BAM file that is converted automatically
      into a BED file using the following command:

        samtools depth -aa input.bam > output.bed

    If the reference is provided, an additional plot showing the coverage versus
    GC content is also shown.

    Here are some examples

        sequana_coverage --input file.bed --window-median 1001
        sequana_coverage --input file.bam --window-median 1001 -r <REFERENCE.fa>

    An other interesting option is to provide a BED file with 4 columns. The
    fourth column being another coverage data created with a filter. One can
    create such a file only from the BAM file using samtools as follows given
    the original unfiltered BAM file named input.bam:

        samtools view -q 35  -o data.filtered.bam input.bam
        samtools depth input.bam data.filtered.bam  -aa > test.bed
        sequana_coverage --input test.bed --show-html

    Note that the first file is the filtered one, and the second file is the
    unfiltered one.


    Note for multi chromosome and genbank features: for now, you will need to call 
    sequana_coverage for each chromosome individually since we accept only one
    genbank as input parameter:

        sequana_coverage --input file.bed --genbank chrom1.gbk -c 1

    chromosome order in the BED and 

        """)

        epilog = purple("""
----

AUTHORS: Thomas Cokelaer, Dimitri Desvillechabrol
Documentation: http://sequana.readthedocs.io
Issues: http://github.com/sequana/sequana
        """)

        description = """DESCRIPTION:
        """

        super(Options, self).__init__(usage=usage, prog=prog,
                description=description, epilog=epilog,
                formatter_class=CustomFormatter)

        # options to fill the config file
        group = self.add_argument_group("Required argument")
        group.add_argument("-i", "--input", dest="input", type=str,
            help=("Input file in BED or BAM format. If a BAM file is "
                 "provided, it will be converted locally to a BED file "
                 "using genomecov, which must be installed."))

        group = self.add_argument_group("Optional biological arguments")
        group.add_argument(
            '-c', "--chromosome", dest="chromosome", type=int, default=0,
            help="Chromosome number (if only one, no need to use: the single"
                 " chromosome is chosen automatically). Default is "
                 " first chromosome found in the BED file. You may want to"
                 " analyse all chromosomes at the same time. If so, set this"
                 " parameter to 0")
        group.add_argument('-o', "--circular", dest="circular",
            default=False, action="store_true",
            help="""If the DNA of the organism is circular (typically
            viruses or bacteria), set to True""")

        group = self.add_argument_group("General")
        group.add_argument("--output-directory", dest="output_directory",
            default="report", help="name of the output (report) directory.")
        group.add_argument('--show-html', dest="show_html", default=False,
            action='store_true',
            help="""When report is created, you can open
            the main page automatically with this option (default is False)""")
        group.add_argument("-q", "--quiet", dest="verbose",
            default=True, action="store_false")
        group.add_argument('--no-report', dest="create_report",
            default=True, action='store_false',
            help="""Do not create any HTML report""")
        group.add_argument("--logging-level", dest="logging_level",
            default="INFO",
            help="set to DEBUG, INFO, WARNING, CRITICAL, ERROR")
        group = self.add_argument_group('Annotation')
        group.add_argument("-b", "--genbank", dest="genbank",
            type=str, default=None, help='a valida genbank annotation')

        # Group related to GC content
        group = self.add_argument_group("GC content related")
        group.add_argument('-r', "--reference", dest="reference", type=str,
            default=None,
            help="""If available, you can provide a reference (ENA/NCBI). It
                 must have the same length as the one used to create the
                 BAM or BED file. If provided, it is used to create the
                 coverage versus GC content image""")
        group.add_argument(
            "-g", "--window-gc", dest="w_gc", type=int, default=201,
            help="""Length of the running window to compute the GC content""")
        group.add_argument('-n', "--nlevels", dest="levels", type=int,
            default=3, help="""Number of levels in the contour""")

        #group running median
        group = self.add_argument_group("Running Median related")
        group.add_argument("-w", "--window-median", dest="w_median", type=int,
            help="""Length of the running median window (default 4001,
                 recommended for viruses).  For long genome, 20001
                 or 30001 is recommended but larger windows may be
                 useful in the presence of long deleted regions.""",
            default=4001)

        group.add_argument("-k", "--mixture-models", dest="k", type=int,
            help="""Number of mixture models to use (default 2, although if sequencing
        depth is below 8, k is set to 1 automatically). To ignore that behaviour
        set k to the required value""",
            default=None)

        group.add_argument("-L", "--low-threshold", dest="low_threshold",
            default=None, type=float,
            help=("lower threshold (zscore) of the confidence interval. "
                "Overwrite value given by --threshold/-T"))
        group.add_argument("-H", "--high-threshold", dest="high_threshold",
            default=None, type=float,
            help=("higher threshold (zscore) of the confidence interval. "
                "Overwrite value given by --threshold/-T"))
        group.add_argument("-T", "--threshold", dest="threshold",
            default=4, type=float,
            help="""set lower and higher thresholds of the confidence interval.""")

        group = self.add_argument_group("Download reference")
        group.add_argument("--download-reference", dest="download_reference",
            default=None, type=str)
        group.add_argument("--download-genbank", dest="download_genbank",
            default=None, type=str)
        group.add_argument("--database", dest="database",
            default="ENA", type=str,
            choices=["ENA", "EUtils"],
            help="Download the reference from one of these database (default ENA)")


def main(args=None):

    if args is None:
        args = sys.argv[:]

    user_options = Options(prog="sequana")

    # If --help or no options provided, show the help
    if len(args) == 1:
        user_options.parse_args(["prog", "--help"])
    else:
        options = user_options.parse_args(args[1:])

    sequana_debug_level(options.logging_level)

    if options.download_reference:
        logger.info("Downloading reference %s from %s\n" %
            (options.download_reference, options.database))

        from bioservices.apps import download_fasta as df
        df.download_fasta(options.download_reference, method=options.database)
        if options.download_genbank is None:
            return

    if options.download_genbank:
        logger.info("Downloading genbank %s from %s\n" %
            (options.download_reference, options.database))
        from sequana.snpeff import download_fasta_and_genbank
        download_fasta_and_genbank(options.download_genbank,
                                   options.download_genbank, 
                                   genbank=True, fasta=False)
        return

    if options.genbank:
        assert os.path.exists(options.genbank), \
            "%s does not exists" % options.genbank

    if options.verbose:
        logger.info("Reading %s. This may take time depending on " 
            "your input file" % options.input)

    # Convert BAM to BED
    if options.input.endswith(".bam"):
        bedfile = options.input.replace(".bam", ".bed")
        if options.verbose:
            logger.info("Converting BAM into BED file")
        shellcmd("bedtools genomecov -d -ibam %s > %s" % (options.input, bedfile))
    elif options.input.endswith(".bed"):
        bedfile = options.input
    else:
        raise ValueError("Input file must be a BAM or BED file")

    # Set the thresholds
    if options.low_threshold is None:
        options.low_threshold = -options.threshold

    if options.high_threshold is None:
        options.high_threshold = options.threshold

    # and output directory
    config.output_dir = options.output_directory
    config.sample_name = os.path.basename(options.input).split('.')[0]

    # Now we can create the instance of GenomeCoverage
    gc = GenomeCov(bedfile, options.genbank, options.low_threshold,
                   options.high_threshold, 0.5, 0.5)

    # if we have the reference, let us use it
    if options.reference:
        logger.info('Computing GC content')
        gc.compute_gc_content(options.reference, options.w_gc,
                              options.circular)

    # Now we scan the chromosomes, 
    if len(gc.chr_list) == 1:
        if options.verbose:
            logger.warning("There is only one chromosome. Selected automatically.")
        chrom = gc.chr_list[0]
        chromosomes = [chrom]
        run_analysis(chrom, options, gc.feature_dict)
    elif options.chromosome <=-1 or options.chromosome > len(gc.chr_list):
        raise ValueError("invalid chromosome index ; must be in [1-{}]".format(len(gc.chr_list)+1))
    else: # chromosome index is zero 
        # For user, we start at position 1 but in python, we start at zero
        if options.chromosome:
            chromosomes = [gc[options.chromosome-1]]
        else:
            chromosomes = gc

        if options.verbose:
            print("There are %s chromosomes/contigs." % len(gc))
            for this in gc.chr_list:
                print("    {}".format(this.chrom_name))

        for i, chrom in enumerate(chromosomes):
            if options.verbose:
                print("==================== analysing chrom/contig %s/%s (%s)"
                      % (i + options.chromosome, len(gc),
                      chrom.chrom_name))
            run_analysis(chrom, options, gc.feature_dict)

    if options.verbose:
        logger.info("Creating report in %s. Please wait" % config.output_dir)

    if options.chromosome:
        cc = options.chromosome - 1
        datatable = CoverageModule.init_roi_datatable(gc[cc])
        ChromosomeCoverageModule(chromosomes[0], datatable, None)
        page = "{0}{1}{2}.cov.html".format(config.output_dir, os.sep,
                                           chrom.chrom_name)
    else:
        CoverageModule(gc)
        page = "{0}{1}coverage.html".format(config.output_dir, os.sep)

    if options.show_html:
        from easydev import onweb
        onweb(page)


def run_analysis(chrom, options, feature_dict):

    if options.verbose:
        print(chrom)

    if options.verbose:
        logger.info('Computing running median (w=%s)' % options.w_median)

    # compute running median
    chrom.running_median(n=options.w_median, circular=options.circular)

    stats = chrom.get_stats(output="dataframe")
    stats.set_index("name", inplace=True)

    DOC = stats.ix['DOC'].Value
    if options.k is None and DOC < 8:
        options.k = 1
    elif options.k is None:
        options.k = 2

    if options.verbose:
        print("Number of mixture model %s " % options.k)
        print('Computing zscore')

    # Compute zscore
    chrom.compute_zscore(k=options.k, verbose=options.verbose)

    # Save the CSV file of the ROIs
    high = chrom.thresholds.high2
    low = chrom.thresholds.low2
    query = "zscore > @high or zscore < @low"
    if feature_dict and chrom.chrom_name in feature_dict:
        f = FilteredGenomeCov(chrom.df.query(query),
                        chrom.thresholds,
                        feature_list=feature_dict[chrom.chrom_name])
    else:
        f = FilteredGenomeCov(chrom.df.query(query), chrom.thresholds)
    directory = options.output_directory 
    directory += os.sep + "coverage_reports" 
    directory += os.sep + chrom.chrom_name
    mkdirs(directory)
    f.df.to_csv("{}/rois.csv".format(directory))

    if options.verbose:
        logger.info("Computing centralness")

    # Let us save the thresholds first and then change it to compute centralness
    thresholds = chrom.thresholds.copy()

    chrom.thresholds.low = -3
    chrom.thresholds.high = 3
    c3 = chrom.get_centralness()

    chrom.thresholds.low = -4
    chrom.thresholds.high = 4
    c4 = chrom.get_centralness()
    chrom.thresholds = thresholds.copy()   # Get back to the original values

    if options.verbose and chrom.thresholds:
        print(chrom.thresholds)

    if options.verbose:
        res = chrom._get_best_gaussian()
        print("sigma and mu of the central distribution: mu=%s, sigma=%s" %
            (round(res["mu"],3), round(res['sigma'],3)))
        print("Evenness: %8.3f" % chrom.get_evenness())
        print("Centralness (3 sigma): %f" % round(c3,3))
        print("Centralness (4 sigma): %f" % round(c4,4))

    if options.verbose:
        print("\n\n")


if __name__ == "__main__":
   import sys
   main()#sys.argv)

