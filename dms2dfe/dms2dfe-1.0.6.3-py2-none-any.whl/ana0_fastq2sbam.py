#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

import sys
from os.path import splitext, exists, basename
import logging
from multiprocessing import Pool
import pandas as pd
import subprocess
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'
from dms2dfe import configure
from dms2dfe.lib.io_seq_files import getusablefastqs_list,fastq2qcd,qcd2sbam
#import numpy as np

def main(prj_dh,test=False):
    """
    **--step 0.2**. Preprocesses and aligns sequencing files.

    The steps and required dependendencies are following. 

    .. code-block:: text

        Quality filtering        : using Trimmomatic.
        Alignment                : using bowtie2
        .sam to .bam conversion  : using samtools

    :param prj_dh: path to project directory
    """
    logging.info("start")
    global trimmomatic_fh,fsta_fh,alignment_type,bt2_ref_fh,bowtie2_fh,samtools_fh,bowtie2_com

    if not exists(prj_dh) :
        logging.error("Could not find '%s'\n" % prj_dh)
        sys.exit()
    configure.main(prj_dh)
    from dms2dfe.tmp import info
    fsta_fh=info.fsta_fh
    cores=info.cores
    trimmomatic_fh=info.trimmomatic_fh
    bowtie2_fh=info.bowtie2_fh
    trimmomatic_com=info.trimmomatic_com
    bowtie2_com=info.bowtie2_com
    samtools_fh=info.samtools_fh
    alignment_type=info.alignment_type

    # make bowtie index
    bt2_ref_fh = splitext(fsta_fh)[0]
    if not exists("%s.1.bt2" % bt2_ref_fh):
        bowtie_ref_com="%s-build --quiet %s %s &> %s.logbt2bld" \
                        % (bowtie2_fh,fsta_fh,splitext(bt2_ref_fh)[0],bt2_ref_fh)
        subprocess.call(bowtie_ref_com,shell=True)
        logging.info("bt2_ref_fh do not exist, made one.")
    fastqs_list=getusablefastqs_list(prj_dh)
    # print fastqs_list
    if len(fastqs_list)!=0:
        if test:
            for fastq in fastqs_list:
                pooled(fastq)
        else:
            pool=Pool(processes=int(cores))  
            pool.map(pooled,fastqs_list)
            pool.close(); pool.join()
    else:
        logging.info("already processed")  
    # cfg_h5.close()
    logging.shutdown()

def pooled(fastq_fhs_list):
    """
    This runs the submodules and used to multi-thread process. 
    
    :param fastq_fhs_list: R1 read of fastq tuple with R1 and R2 if otherwise paired.    
    """
    fastq2qcd(fastq_fhs_list,trimmomatic_fh)
    qcd2sbam(fastq_fhs_list,fsta_fh,alignment_type,bt2_ref_fh,bowtie2_fh,samtools_fh,bowtie2_com=bowtie2_com)

if __name__ == '__main__':
    if len(sys.argv)==3:
        test=sys.argv[2]
    else:
        test=False
    main(sys.argv[1],test=test)