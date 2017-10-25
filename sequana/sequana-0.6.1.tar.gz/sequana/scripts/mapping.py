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
from snakemake import shell as  shellcmd
import shutil
import glob
import sys
from optparse import OptionParser
import argparse


class Options(argparse.ArgumentParser):
    def  __init__(self, prog="sequana_mapping"):
        usage = """Welcome to SEQUANA - mapping standalone

            sequana_mapping --file1 R1.fastq --file2 R2.fastq --reference reference

    This is a simple mapper for quick test. The commands are as follows::

        # Indexing
        bwa index REFERENCE
        samtools faidx REFERENCE

        # mapping
        bwa_mem -t 4 -R @RG\\tID:1\\tSM:1\\tPL:illumina -T 30 REFERENCE FASTQ_FILES  | samtools 
        view -Sbh -> REFERENCE.bam

        samtools sort -o REFERENCE.sorted.bam  REFERENCE.bam 



AUTHORS: Sequana Consortium
Documentation: http://sequana.readthedocs.io
Issues: http://github.com/sequana/sequana
        """
        description = """DESCRIPTION:


        """

        super(Options, self).__init__(usage=usage, prog=prog,
                description=description)

        # options to fill the config file
        self.add_argument("--file1", dest="file1", type=str,
            default=None, required=True,
            help="""R1 fastq file (zipped) """)
        self.add_argument("--file2", dest="file2", type=str,
            default=None,
            help="""R2 fastq file (zipped) """)
        self.add_argument("--reference", dest="reference", type=str,
            help="""reference """)
        self.add_argument("--thread", dest="thread", type=int, default=4,
            help="""number of threads """)
        self.add_argument("--pacbio", dest="pacbio", action="store_true",
            default=False,
            help="""specific pacbio parameters recommended by bwa mem are used """)
        self.add_argument("--use-sambamba", dest="sambamba", action="store_true",
            default=False,
            help="""use sambamba instead of samtools for the sorting """)


def main(args=None):

    if args is None:
        args = sys.argv[:]

    user_options = Options(prog="sequana")

    # If --help or no options provided, show the help
    if len(args) == 1:
        user_options.parse_args(["prog", "--help"])
    else:
       options = user_options.parse_args(args[1:])


    reference = options.reference
    if options.file1 and options.file2:
        fastq = "%s %s" % (options.file1, options.file2)
    elif options.file1 and not options.file2:
        fastq = "%s" % (options.file1)
    elif options.file1 is None:
        raise ValueError("--file1 must be used")

    from sequana import FastQ
    from sequana import FastA
    S = 0
    for this in FastQ(options.file1):
        S += len(this['sequence'])
    if options.file2:
        for this in FastQ(options.file2):
            S += len(this['sequence'])
    ref = FastA(options.reference)
    coverage = float(S) / len(ref.sequences[0])
    print('Theoretical Depth of Coverage : %s' % coverage)

    params = {"reference": reference, "fastq": fastq, "thread": options.thread}

    # indexing
    shellcmd("bwa index %(reference)s " % params)
    cmd = "samtools faidx %(reference)s " % params

    # mapping
    cmd = "bwa mem -M "  # mark shorter split read as secondary; -M is not compulsary but recommended
    if options.pacbio:
        cmd += "-x pacbio "
    cmd += r" -t %(thread)s -R @RG\\tID:1\\tSM:1\\tPL:illumina -T 30 %(reference)s %(fastq)s  "

    # Samtools options:
    #   S:ignore input format
    #   h:include header
    #   b:bam output
    if options.sambamba is False:
        cmd += "| samtools view -Sbh | "
        # sorting BAM
        cmd += "samtools sort -@ %(thread)s -o %(reference)s.sorted.bam -"
        shellcmd(cmd % params)
    else:
        # FIXME use sambamba for the view as well
        cmd += "| samtools view -Sbu - | sambamba sort /dev/stdin -o %(reference)s.sorted.bam -t %(thread)s  --tmpdir=./tmp  " % params
        shellcmd(cmd % params)



"""reference = "JB409847"
fastq = "Cherry-1_S7_L001_R1_cutadapt_trim_1.fq"

params = {"reference": reference, "fastq": fastq}

shellcmd("bwa index %(reference)s.fa" % params)
cmd = "samtools faidx %(reference)s.fa" % params
shellcmd(r"bwa mem -t 4 -R @RG\\tID:1\\tSM:1\\tPL:illumina -T 30 %(reference)s.fa %(fastq)s  | samtools view -Sbh -> %(reference)s.bam" % params)

shellcmd("samtools sort -o %(reference)s.sorted.bam  %(reference)s.bam" % params)
"""



