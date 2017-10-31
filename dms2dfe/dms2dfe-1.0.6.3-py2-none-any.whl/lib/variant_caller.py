#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

"""
================================
``io_data_files``
================================
"""
from os import stat,makedirs
from os.path import splitext, exists,basename,dirname,expanduser
import numpy as np
import pandas as pd
import pysam
import logging
import subprocess
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..):%(lineno)d: %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'
from dms2dfe.lib.global_vars import cds_64

# # DEFS
def getusablesbams_list(prj_dh):
    """
    This detects sorted bam files that can be further processed for variant calling.
    
    :param prj_dh: path to project directory.
    """
    
    lbls=pd.read_csv(prj_dh+'/cfg/lbls')
    lbls=lbls.set_index('varname')
    sbam_fhs=[] # for list of sbams for pool
    for lbli,lbl in lbls.iterrows() :
        # if fh are fastq : find sbam 
        sbam_fh=str(lbl['fhs_1'])
        sbam_fh=expanduser(sbam_fh)
        #print sbam_fh
        if not (exists(sbam_fh+".list_mut_cds") & exists(sbam_fh+".mat_mut_cds")) :    
            ext=splitext(sbam_fh)[1]              
            if (("fastq" or "fq") in ext):
                if (exists(sbam_fh+".sam.s.bam")):
                    sbam_fh=sbam_fh+".sam.s.bam"                
                elif exists(sbam_fh+".qcd.fastq.sam.s.bam") :
                    sbam_fh=sbam_fh+".qcd.fastq.sam.s.bam"
                else :
                    logging.warning("can not find: %s" % sbam_fh)     
            # if (("s.bam" in sbam_fh) and (exists(sbam_fh))) and (not exists(sbam_fh+".mat_mut_cds") or (stat(sbam_fh+".mat_mut_cds").st_size ==0)):
            if ((sbam_fh.endswith("s.bam")) and (exists(sbam_fh))) and (not exists(sbam_fh+".mat_mut_cds") or (stat(sbam_fh+".mat_mut_cds").st_size ==0)):
                sbam_fhs.append(sbam_fh)              
            else: 
                logging.info("already processed: %s" % basename(sbam_fh))
        else :
            logging.info("already processed: %s" % basename(sbam_fh))
            if not exists('%s/data_mutmat' % prj_dh):
                makedirs('%s/data_mutmat' % prj_dh)
            com="cp %s.mat_mut_cds %s/data_mutmat/%s.mat_mut_cds" % (sbam_fh,prj_dh,basename(sbam_fh))
            # print com
            subprocess.call(com,shell=True)
    return sbam_fhs

def qual_chars2nums(qual_chars,qual_format):
    """
    This converts the phred qualities from the ASCII format to numbers.
    
    :param qual_chars: phred score in ASCII format (str).
    :param qual_format: phred score in numbers (list).
    """
    # format : 33 or 64 
    qual_nums = []
    for char in qual_chars.rstrip('\n'):
        qual_nums.append(ord(char) - qual_format)
        #print('quality is ' + str(qual_nums))
    return qual_nums   

def is_qry_alind_useful(qry_alind,Q_cutoff) :
    """
    This detects whether a read passes a number of criterias eg. Phred quality score. 

    .. code-block:: text

        cigar dode | descr | col index
        M  BAM_CMATCH  0
        I  BAM_CINS    1
        D  BAM_CDEL    2
        N  BAM_CREF_SKIP   3
        S  BAM_CSOFT_CLIP  4
        H  BAM_CHARD_CLIP  5
        P  BAM_CPAD    6
        =  BAM_CEQUAL  7
        X  BAM_CDIFF   8

    :param qry_alind: aligned query sequnce.
    :param Q_cutoff: cut off of average phred score per read.
    """
    # need has_tag here
    qry_tags=qry_alind.tags
    for qry_tag in qry_tags :
        if (qry_tag[0]=='NM' and qry_tag[1]==0) :
            return False
            break            
    else :    
        qry_qual_mean=np.mean(qual_chars2nums(qry_alind.qual,33))
        if not qry_qual_mean>=Q_cutoff : ## cut2 : if avg q score >= 30        
            return False 
        else :
            ## cut3 : N D I ;  
            if "N" in qry_alind.seq :
                return False
            else :
                #for cigar_tuple in qry_alind.cigar :  ## if DorI > 3 : false;
                cig_list_lbl=[cigar_tuple[0] for cigar_tuple in qry_alind.cigar]
                cig_list_num=[cigar_tuple[1] for cigar_tuple in qry_alind.cigar]
                if (1 or 2) in cig_list_lbl :
                    if (1 and 2) in cig_list_lbl :  ## if D&I exist
                        if cig_list_num[cig_list_lbl.index(1)]-cig_list_num[cig_list_lbl.index(1)]==0 :    ## diff of numbers = 0
                            return True
                        else :
                            return False        
                    else :                         ## rest if any D or I s : False
                        return False 
                else :
                    return True

def get_mut_cds(qry_alind,fsta_seq,list_mut_cds_fh,Q_cutoff) :
    """
    This gets the mutations at codon level.
    
    :param qry_alind: aligned query sequnce.
    :param fsta_seq: sequence of reference DNA (str).
    :param list_mut_cds_fh: path to file with codon level list of mutations. 
    :param Q_cutoff: cut off of average phred score per read.
    """
    from dms2dfe.lib.global_vars import cds_64
    
    qry_seq_ini_offset=3-np.remainder(qry_alind.pos,3)     # to be used for both qry and ref
    # nts to skip at start; make it 0 based bcz rest all is _; ingnore initial nts before codon starts; pos is zero based
    #pos= number of nts before the place. if rem is 0 = offset =0, 1=1, 2=2
    #if pos rem=2 : offset=1; 3:0; 1:2
    if qry_seq_ini_offset==3 :
        qry_seq_ini_offset=0
    qry_seq_len=int(np.floor((qry_alind.qlen)/3)*3)    # ignore trailing nts ie. last incomplete codon  
    qry_seq_S_offset=qry_alind.qstart # for qry only (where S's are ignored). 'S'oft clips (4)            
    qry_seq = qry_alind.seq[qry_seq_ini_offset+qry_seq_S_offset:qry_seq_len++qry_seq_S_offset]   #[qry_alind.qstart:qry_alind.qend]
    ref_seq = str(fsta_seq[qry_alind.pos+qry_seq_ini_offset:qry_alind.pos+qry_seq_len])
    qry_qual= qual_chars2nums(qry_alind.qual[qry_seq_ini_offset+qry_seq_S_offset:qry_seq_len++qry_seq_S_offset],33)
    if len(ref_seq)==len(qry_seq) : #deprecate
        if np.remainder(qry_seq_len,3) ==0 : #deprecate
            qry_cds_len=int(qry_seq_len/3.)
            qry_cdi_offset=int(np.ceil(qry_alind.pos/3.))+1 # according to chromosome
            if qry_seq_ini_offset !=0 :
                qry_cds_len=qry_cds_len-2    
            for qry_cdi in range(0, qry_cds_len) : # loop over qry
                qry_cd=qry_seq[qry_cdi*3:qry_cdi*3+3] # atomise seq -> codons
                ref_cd=ref_seq[qry_cdi*3:qry_cdi*3+3] # atomise seq -> codons
                if not qry_cd == ref_cd :
                    qry_cd_qual_mean=np.mean(qry_qual[qry_cdi*3:qry_cdi*3+3])
                    if qry_cd_qual_mean>=Q_cutoff :
                        #print ref_cd, qry_cd 
                        mut_cd = [qry_alind.qname,str(qry_cdi+qry_cdi_offset),str(cds_64.index(qry_cd)),str(ref_cd),str(qry_cd)]
                        if not pd.isnull(mut_cd).any() :
                            list_mut_cds_fh.write("\t".join(mut_cd)+"\n")
    #                     else :
    #                         logging.error("%s @ if not pd.isnull" % qry_alind.qname)
    #     else :
    #         logging.error("%s @ if np.remainder(qry_seq_len,3)" % qry_alind.qname)
    # else :
    #     logging.error("%s @ if len(ref_seq)==len(qry_seq)" % qry_alind.qname)
        
def sam2mutmat(sbam_fh,fsta_id,fsta_seqlen,fsta_seq,cds_ref,Q_cutoff,prj_dh):        
    """
    This converts sorted .bam file to codon level mutation matrix (.mat_mut_cds)
    
    :param sbam_fh: path to sorted bam file (str).
    :param fsta_id: name of reference (from .fasta file) (str). 
    :param fsta_seqlen: length of reference sequnce (int).
    :param fsta_seq: reference sequnce (str).
    :param cds_ref: codons in refernce sequnce (list)
    :param Q_cutoff: cut off of average phred score per codon.
    """
    list_mut_cds_fh_str=sbam_fh+".list_mut_cds"
    list_mut_cds_fh=open(list_mut_cds_fh_str,"w")
    list_mut_cds_fh.write("qry_id\tcdi\tcd_type\tref_cd\tqry_cd\n")
    list_mut_cds_dedup_fh=open(list_mut_cds_fh_str+"_dedup","w")
    #list_mut_cds_dedup_fh.write("qry_id\tcdi\tcd_type\tref_cd\tqry_cd\n")
    mat_mut_cds_fh_str=sbam_fh+".mat_mut_cds"
    mat_mut_cds_fh=open(mat_mut_cds_fh_str,"w")
    
    ## ITERATE OVER SBAM FILE && GET MUT_LIST
    alins_all = pysam.Samfile(sbam_fh, "rb")
    qrys_alind = alins_all.fetch(fsta_id, 0, fsta_seqlen)
    for qry_alind in qrys_alind :  
        if is_qry_alind_useful(qry_alind,Q_cutoff) :
            #print qry_alind.qname 
            # logging.info("'%s'" % qry_alind.qname)
            get_mut_cds(qry_alind,fsta_seq,list_mut_cds_fh,Q_cutoff)
    list_mut_cds_fh.close
    
    ### OPEN LIST AND MAKE A MAT
    list_mut_cds_fh=open(sbam_fh+".list_mut_cds","r")     
    mut_cds_list_df_dups=pd.read_csv(list_mut_cds_fh_str,sep="\t") # open list for reading
    ## remove dupticate rows for exclusively sm
    mut_cds_list_df_dedups=mut_cds_list_df_dups.groupby('qry_id').size() == 1
    mut_cds_list_df_dups=mut_cds_list_df_dups.set_index('qry_id')
    mut_cds_list_df=mut_cds_list_df_dups.loc[mut_cds_list_df_dedups,:]
    mut_cds_list_df=mut_cds_list_df.reset_index()
    mut_cds_list_df.to_csv(list_mut_cds_dedup_fh)
    list_mut_cds_dedup_fh.close
    ## cols: qry_id cdi cd_type ref_cd qry_cd
    ## rows: 0 to end
    mut_cds_mat_df=pd.DataFrame(columns=cds_64,index=range(1,fsta_seqlen/3+1))
    for index, mut_cdi in mut_cds_list_df.iterrows():
        #print mut_cdi
        if pd.isnull(mut_cds_mat_df.ix[mut_cdi.loc["cdi"],mut_cdi.loc["qry_cd"]]) :
            mut_cds_mat_df.ix[mut_cdi.loc["cdi"],mut_cdi.loc["qry_cd"]]=1
        else :
            mut_cds_mat_df.ix[mut_cdi.loc["cdi"],mut_cdi.loc["qry_cd"]]+=1 # row, column    
    mut_cds_mat_df.insert(0,'ref_cd',cds_ref)
    mut_cds_mat_df.loc[:,"refi"]=range(1,len(mut_cds_mat_df)+1)
    mut_cds_mat_df.to_csv(mat_mut_cds_fh_str)  
    mut_cds_mat_fh="%s/data_mutmat/%s" % (prj_dh,basename(mat_mut_cds_fh_str))
    if not exists(dirname(mut_cds_mat_fh)):
        try:
            makedirs(dirname(mut_cds_mat_fh))
        except :
            a=1
    mut_cds_mat_df.to_csv(mut_cds_mat_fh)
    # logging.info("OTPTS:\t'%s' " % list_mut_cds_fh_str)
    logging.info("output: %s" % basename(mat_mut_cds_fh_str))
        