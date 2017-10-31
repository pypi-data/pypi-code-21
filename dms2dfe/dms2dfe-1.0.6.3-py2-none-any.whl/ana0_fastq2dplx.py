#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.    

from os.path import exists,basename
import sys
import pandas as pd
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'
from dms2dfe import configure
from dms2dfe.lib.io_seq_files import fastq2qcd,fastq2dplx

def main(prj_dh):
    """
    **--step 0.1**. Demultipexes .fastq files based on barcodes located at `prj_dh/cfg/barcodes`.

    :param prj_dh: path to project directory
    """
    logging.info("start")
    if not exists(prj_dh) :
        logging.error("Could not find '%s'\n" % prj_dh)
        sys.exit()
    configure.main(prj_dh)
    from dms2dfe.tmp import info
    trimmomatic_fh=info.trimmomatic_fh

    if exists('%s/cfg/barcodes' % prj_dh) :
        barcodes=pd.read_csv(prj_dh+'/cfg/barcodes')
        # print barcodes        
        if len(barcodes)!=0:
            fastq_R1_fhs=[str(s) for s in barcodes.loc[:,'fastq_R1_fh'].unique()]
            fastq_fhs_list=[[s, s.replace('R1','R2')] for s in fastq_R1_fhs if not exists("%s.qcd.fastq" % s)] # pairs
            for fastq_fhs_tp in fastq_fhs_list:
                fastq2qcd(fastq_fhs_tp,trimmomatic_fh)
#             fastq_R1_fhs=[fastq_R1_fh+".qcd.fastq" for fastq_R1_fh in fastq_R1_fhs if not ".qcd." in fastq_R1_fh]
            barcodes=barcodes.set_index('fastq_R1_fh')
            for fastq_R1_fh in fastq_R1_fhs:
                if exists(fastq_R1_fh):
                    fastq_R1_fh_barcodes=barcodes.loc[fastq_R1_fh,:]
                    fastq_R2_fh=fastq_R1_fh.replace('R1','R2') #str(fastq_R1_fh_barcodes.ix[0,'fastq_R2_fh'])
                    if (not exists("%s.qcd.fastq_unresolved_joined.qcd.fastq" % (fastq_R1_fh)))\
                    and (not exists("%s.qcd.fastq_unresolved_joined.qcd.fastq" % (fastq_R1_fh))):
                        if exists(fastq_R1_fh):
                            logging.info("processing: %s" % basename(fastq_R1_fh))
                            # print fastq_R1_fh_barcodes
                            barcode_R1s=[str(s) for s in list(fastq_R1_fh_barcodes.loc[:,'barcode_R1'])]
                            barcode_R2s=[str(s) for s in list(fastq_R1_fh_barcodes.loc[:,'barcode_R2'])]        
                            fastq_fns    =[str(s) for s in list(fastq_R1_fh_barcodes.loc[:,'fastq_fn'])]        
                            fastq2dplx(fastq_R1_fh+".qcd.fastq",fastq_R2_fh+".qcd.fastq",\
                                       barcode_R1s,barcode_R2s,fastq_fns)
                        else:
                            logging.info("fastq_R2_fh do not exist: %s" % fastq_R2_fh)
                    else:
                        logging.info("already done : %s" % fastq_R1_fh)        
                else:
                    logging.info("fastq_R1_fh do not exist: %s" % fastq_R1_fh)
        else:
            logging.info("skipping: because barcodes not present in cfg")        
    else:
        logging.info("skipping: because barcodes not present in cfg")        
    logging.shutdown()

if __name__ == '__main__':
    main(sys.argv[1])