#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

"""
================================
``io_mut_files``
================================
"""
from __future__ import division
import sys
from os.path import splitext,exists,basename,abspath,dirname
from os import makedirs,stat
import pandas as pd
import numpy as np
from glob import glob
import logging
import subprocess

logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..):%(lineno)d: %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'
from dms2dfe.lib.fit_curve import fit_gauss_params
from dms2dfe.lib.global_vars import aas_21,cds_64,mut_types_form,mut_types_NorS
from dms2dfe.lib.convert_seq import cds2aas
from dms2dfe.lib.io_seq_files import getdepth_cds,getdepth_ref
from dms2dfe.lib.io_data_files import getusable_lbls_list,getusable_fits_list,getusable_comparison_list
from dms2dfe.lib.io_dfs import concat_cols,fhs2data_combo,debad,set_index
from dms2dfe.lib.io_nums import str2num,plog
from dms2dfe.lib.io_stats import testcomparison,multipletests

def makemutids(data_lbl,refis):
    """
    This makes the mutation ids eg. M001T or A024T from mutation matrix.
    
    :param data_lbl: dataframe with columns of reference (`ref`) and mutation (`mut`).
    :param refis: index of reference amino acids/ codons.
    :returns mutids: list of mutation ids.
    """
    mutids=[]
    data_lbl=data_lbl.reset_index()
    reflen=len(refis)
    for muti in range(len(data_lbl)//reflen):
        refii=0
        for refi in refis:
            mutids.append("%s%03d%s" % (data_lbl.loc[muti*reflen+refii,'ref'],refi,data_lbl.loc[muti*reflen+refii,'mut']))
            refii+=1
    if len(data_lbl)!=len(mutids):
        logging.error("len(data_lbl)!=len(mutids) bcz %d != %d" % (len(data_lbl),len(mutids)))
        sys.exit()
    return mutids    

def makemutids_fromprtseq(prt_seq,muts=None):
    refs=list(prt_seq)
    refis=range(1,len(refs)+1,1)
    if muts is None:
        from dms2dfe.lib.global_vars import aas_21
        muts=aas_21
    mutids=[]
    for i in range(len(refs)):
        for mut in muts: 
            mutid="%s%03d%s" % (refs[i],refis[i],mut)
            mutids.append(mutid.replace('*','X'))
    return mutids


def mutids_converter(mutids,out,type_form):
    if type_form=='aas':
        offset=0
    elif type_form=='cds':
        offset=2
        
    if out=='refi':
        return [str2num(mutid) for mutid in mutids]    
    elif out=='ref':
        return [mutid[:1+offset] for mutid in mutids]
    elif out=='mut':
        return [mutid[-1-offset:] for mutid in mutids]
    elif out=='refrefi':
        return [mutid[:4+offset] for mutid in mutids]

def mat_cds2mat_aas(mat_cds,host) :
    """
    This converts mutation matrix of codon to that of amino acid.
    
    :param mat_cds: codon level mutation matrix.
    :param host: name of host organism for choosing codon table. [coli | yeast | sapiens].
    :returns mat_aas: amino acid level mutation matrix.
    """
    aas_wt=[cds2aas(cd,host) for cd in list(mat_cds.index)]
    aas_64=[cds2aas(cd,host) for cd in list(mat_cds.columns)]
    mat_aas_64 =mat_cds.fillna(0)
    mat_aas_64.columns=aas_64
    mat_aas=mat_aas_64.groupby(mat_aas_64.columns, axis=1).sum()
    mat_aas    =mat_aas.loc[:,aas_21]
    mat_aas.index=aas_wt
    mat_aas.columns.name='mut'
    mat_aas.index.name='ref'
    return mat_aas

def getNS(data_all) : # data (col): can be cds or aas
    """
    This function separates the non-synonymous(N) and synonymous(S) mutations.
    
    :param data_all: dataframe with frequency of mutations (`data_lbl`).
    :returns data_NS: dataframe with non-synonymous(N) and synonymous(S) mutations.
    """
    data_NS=pd.DataFrame(columns=['NiS','NiN'],index=data_all.index);#data_NS.loc[:,'mutids']=data_all.loc[:,'mutids']
    #data_S=pd.DataFrame(columns=data_all.columns,index=data_all.index);data_S.loc[:,'mutids']=data_all.loc[:,'mutids']
    rowcount=0
    for rowi,row in data_all.iterrows() :
        if rowi[0]== rowi[1] :
            data_NS.ix[rowcount,'NiS']=data_all.ix[rowcount,'NiA']    
        else :
            data_NS.ix[rowcount,'NiN']=data_all.ix[rowcount,'NiA']
        rowcount+=1    
    return data_NS

def collate_cctmr(lbl_mat_cds,cctmr):    
    """
    If the reference sequence is a concatamer, this function collates the repeating mutation matrix. 
    
    :param lbl_mat_cds: codon level mutation matrix.
    :param cctmr: tuple with (1-based) boundaries of concatamers.
    :returns lbl_mat_cds: collated codon level mutation matrix.
    """
    if (lbl_mat_cds.index.values[(cctmr[0][0]-1)] == lbl_mat_cds.index.values[(cctmr[1][0]-1)]) and \
    (lbl_mat_cds.index.values[(cctmr[0][1]-1)] == lbl_mat_cds.index.values[(cctmr[1][1]-1)]):
        lbl_mat_cds_cctmr1=lbl_mat_cds.iloc[(cctmr[0][0]-1):(cctmr[0][1]-1),:]
        lbl_mat_cds_cctmr2=lbl_mat_cds.iloc[(cctmr[1][0]-1):(cctmr[1][1]-1),:]
        lbl_mat_cds=lbl_mat_cds_cctmr1.fillna(0)+lbl_mat_cds_cctmr2.fillna(0)
	#print lbl_mat_cds.index.name
	#print lbl_mat_cds.columns.tolist()
        lbl_mat_cds.loc[:,"refi"]=lbl_mat_cds_cctmr1.loc[:,"refi"]
    else:
        logging.error("cctmr do not conform %s!=%s or %s!=%s" % (lbl_mat_cds.index.values[(cctmr[0][0]-1)], \
                                                                 lbl_mat_cds.index.values[(cctmr[1][0]-1)], \
                                                                 lbl_mat_cds.index.values[(cctmr[0][1]-1)], \
                                                                 lbl_mat_cds.index.values[(cctmr[1][1]-1)]))
    return lbl_mat_cds.replace(0,np.nan)

def transform_data_lbl(prj_dh,transform_type,
                      type_form='aas',data_lbl_col='NiA_norm',):
    data_lbl_fhs=glob("%s/data_lbl/aas/*" % prj_dh)
    if len(data_lbl_fhs)>0:
        col_sep="."
        data_lbl_all=fhs2data_combo(data_lbl_fhs,cols=[data_lbl_col],index='mutids',col_sep=col_sep)
        data_lbl_all_dh='%s/data_lbl/%s_all' % (prj_dh,type_form)
        if not exists(data_lbl_all_dh):
            makedirs(data_lbl_all_dh)
        data_lbl_all_fh='%s/%s.csv' % (data_lbl_all_dh,data_lbl_col)
        data_lbl_all.to_csv(data_lbl_all_fh)

        if (transform_type=='log2') or (transform_type=='log'):
            data_lbl_all=data_lbl_all.apply(np.log2)
        elif transform_type=='plog':
            data_lbl_all=data_lbl_all.apply(plog)
        else:
            logging.error("trnaform_type not valid: %s" % transform_type)
            sys.exist()
        data_lbl_col='NiA_tran'
        data_lbl_all_fh='%s/%s.csv' % (data_lbl_all_dh,data_lbl_col)
        data_lbl_all.to_csv(data_lbl_all_fh)
        
        for col in data_lbl_all:
            data_lbl_fn,tmp=col.split('.')
            data_lbl_fh='%s/data_lbl/%s/%s' % (prj_dh,type_form,data_lbl_fn)
            data_lbl=pd.read_csv(data_lbl_fh).set_index('mutids')
            if not data_lbl_col in data_lbl:
                data_lbl_cols=data_lbl.columns.tolist()
                data_lbl=pd.concat([data_lbl,
                                    data_lbl_all.loc[:,col]],axis=1)
                data_lbl.columns=data_lbl_cols+[data_lbl_col]
                data_lbl.index.name='mutids'
                data_lbl.to_csv(data_lbl_fh)
        
def transform_data_lbl_deseq(prj_dh,transform_type,rscript_fh,type_form='aas'):
    data_lbl_fhs=glob("%s/data_lbl/aas/*" % prj_dh)
    data_lbl_col='NiA_norm'
    col_sep="."
    data_lbl_all=fhs2data_combo(data_lbl_fhs,cols=[data_lbl_col],index='mutids',col_sep=col_sep)
    data_lbl_all_dh='%s/data_lbl/%s_all' % (prj_dh,type_form)
    if not exists(data_lbl_all_dh):
        makedirs(data_lbl_all_dh)
    data_lbl_all_fh='%s/%s.csv' % (data_lbl_all_dh,data_lbl_col)
    # data_lbl_all=debad(data_lbl_all,axis=0,condi='any',bad='nan')
    # #psudocount to avoid all zero error
    # data_lbl_all=data_lbl_all.fillna(0)
    # data_lbl_all=data_lbl_all+0.5 
    data_lbl_all.to_csv(data_lbl_all_fh)

    data_lbl_tran_col='NiA_tran'
    data_lbl_all_tran_fh='%s/%s.csv' % (data_lbl_all_dh,data_lbl_tran_col)
    if not exists(data_lbl_all_tran_fh):
        data_lbl_all_tran=pd.DataFrame(index=data_lbl_all.index)
        data_lbl_all_tran.index.name='mutids'
        repli=pd.read_csv('%s/cfg/repli' % prj_dh).set_index('varname')
        for avg in repli.index:
            avg_col="%s%s%s" % (avg,col_sep,data_lbl_col)
            if transform_type=='rlog':
                data_lbl_tran_fh="%s/%s.deseq2_annot.csv.deseq2_rld.csv" % (data_lbl_all_dh,avg_col)
            elif transform_type=='vst':
                data_lbl_tran_fh="%s/%s.deseq2_annot.csv.deseq2_vsd.csv" % (data_lbl_all_dh,avg_col)
            if not exists(data_lbl_tran_fh):
                data_deseq2_annot=pd.DataFrame(columns=['condition','type','number of lanes','total number of reads','exon counts'])
                data_deseq2_annot.index.name='file'
                data_deseq2_annot_fh='%s/%s.deseq2_annot.csv' % (data_lbl_all_dh,avg_col)
                data_deseq2_count=pd.DataFrame()
                data_deseq2_count_fh='%s/%s.deseq2_count.csv' % (data_lbl_all_dh,avg_col)
                for rep in repli.loc[avg,:]:
                    if not pd.isnull(rep):
                        rep_col="%s%s%s" % (rep,col_sep,data_lbl_col)
                        data_deseq2_annot.loc[rep_col,'condition']=rep
                        if len(data_deseq2_count)==0:
                            data_deseq2_count=pd.DataFrame(data_lbl_all.loc[:,rep_col].copy())
                        else:
                            data_deseq2_count.loc[:,rep_col]=data_lbl_all.loc[:,rep_col]
                # data_deseq2_annot_index_all=["%s%s%s" % (basename(fh),col_sep,data_lbl_col) \
                #                              for fh in data_lbl_fhs if (basename(fh) not in repli.index)]
                # data_deseq2_annot_index_no_reps=[i for i in data_deseq2_annot_index_all if (i not in data_deseq2_annot.index)]
                # for idx in data_deseq2_annot_index_no_reps:
                #     data_deseq2_annot.loc[idx,'condition']=idx
                data_deseq2_annot.to_csv(data_deseq2_annot_fh)
                data_deseq2_count=debad(data_deseq2_count,axis=0,condi='any',bad='nan')
                data_deseq2_count.to_csv(data_deseq2_count_fh)            
                deseq_fh="%s/deseq2.R" % (abspath(dirname(__file__)))
                log_fh="%s.log" % data_deseq2_annot_fh
                with open(log_fh,'a') as log_f:
                    deseq2_com='%s %s %s %s 1' % (rscript_fh,deseq_fh,data_deseq2_count_fh,data_deseq2_annot_fh)
                    # print deseq2_com
                    subprocess.call(deseq2_com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)              
            data_lbl_tran=pd.read_csv(data_lbl_tran_fh).set_index('Unnamed: 0')
            data_lbl_tran.index.name='mutids'
            if len(data_lbl_all_tran)==0:
                data_lbl_all_tran=data_lbl_tran.copy()
            else:
                data_lbl_all_tran=data_lbl_all_tran.join(data_lbl_tran)
            # print data_lbl_all_tran.columns.tolist()
            # print len(data_lbl_all_tran)
        if len(data_lbl_all_tran.columns.tolist())>0:
            data_lbl_all_tran.to_csv(data_lbl_all_tran_fh)
        else:
            logging.error('transform_type can not be %s: no replicates found' % transform_type)
            sys.exit()
    else:        
        data_lbl_all_tran=pd.read_csv(data_lbl_all_tran_fh).set_index('mutids')

    data_lbl_tran_col='NiA_tran'    
    for col in data_lbl_all_tran:
        data_lbl_fn,tmp=col.split('.')
        data_lbl_fh='%s/data_lbl/%s/%s' % (prj_dh,type_form,data_lbl_fn)
        data_lbl=pd.read_csv(data_lbl_fh).set_index('mutids')
        if not data_lbl_tran_col in data_lbl:
            data_lbl_cols=data_lbl.columns.tolist()
            data_lbl=data_lbl.join(data_lbl_all_tran.loc[:,col])
            data_lbl.columns=data_lbl_cols+[data_lbl_tran_col]
            data_lbl.index.name='mutids'
            data_lbl.to_csv(data_lbl_fh)


def mut_mat_cds2data_lbl(lbli,lbl_mat_mut_cds_fh,
                    host,prj_dh,reflen,cctmr,Ni_cutoff,fsta_fh,clips=None):
    """
    This function converts mutation matrix (produced from .mat) file into data_lbl format.
    
    :param lbli: name of the sample.
    :param lbl_mat_mut_cds_fh: path to codon level mutation matrix (.mat_mut_cds).
    :param host : name of host organism for choosing codon table. (coli | yeast | sapiens).
    :param prj_dh: path to project directory.
    :param reflen: nucleotide level length of the reference sequence.
    :param cctmr: tuple with (1-based) boundaries of concatamers.
    :param Ni_cutoff: threshold of depth per codon to be processed further. 
    """
    if stat(lbl_mat_mut_cds_fh).st_size != 0 :
        lbl_mat_cds=pd.read_csv(lbl_mat_mut_cds_fh) # get mat to df
        # print lbl_mat_mut_cds_fh
        # print lbl_mat_cds.columns.tolist()
        if 'ref_cd' in lbl_mat_cds:
            lbl_mat_cds=lbl_mat_cds.set_index("ref_cd",drop=True) # make codons as the index
        if 'ref' in lbl_mat_cds:
            lbl_mat_cds=lbl_mat_cds.set_index("ref",drop=True) # make codons as the index
        if 'Unnamed: 0' in lbl_mat_cds.columns:
            del lbl_mat_cds['Unnamed: 0']
        lbl_mat_cds.columns.name='mut'
        lbl_mat_cds.index.name='ref'
        if cctmr != None:
            reflen=(cctmr[0][1]-1)*3
            if len(lbl_mat_cds)>reflen*1.25:
                lbl_mat_cds=collate_cctmr(lbl_mat_cds,cctmr)
        lbl_mat_aas=mat_cds2mat_aas(lbl_mat_cds,host)# convert to aa data
        # lbl_mat_cds.to_csv('test')
        for type_form in mut_types_form : # get aas or cds  
            if not exists("%s/data_lbl/%s/%s" % (prj_dh,type_form,str(lbli))):
                # print lbl_mat_aas.tail(10)
                if type_form=="aas":
                    data_lbl=pd.DataFrame(lbl_mat_aas.unstack())
                elif type_form=="cds":
                    data_lbl=pd.DataFrame(lbl_mat_cds.drop("refi",axis=1).unstack())
                # print data_lbl.iloc[170:180,:]
                ref_prt_len=(float(reflen)//3)
                if (len(data_lbl)//ref_prt_len==21) or (len(data_lbl)//ref_prt_len==64):
                    data_lbl.columns=["NiA"]  # rename col Ni  
                    data_lbl.loc[:,'mutids']=makemutids(data_lbl,lbl_mat_cds.loc[:,"refi"]) # add mutids
                    data_lbl=pd.concat([data_lbl,getNS(data_lbl)], axis=1)
                    
                    for type_NorS in mut_types_NorS : # N OR S  
                        data_lbl.loc[:,('Ni%scut' % type_NorS)]=data_lbl.loc[:,'Ni%s' % type_NorS]
                        data_lbl.loc[data_lbl.loc[:,('Ni%scut' % type_NorS)]<Ni_cutoff,('Ni%scut' % type_NorS)]=np.nan \
                        #Ni_cutoff=8 varscan default
                        data_lbl.loc[:,('Ni%scutlog' % type_NorS)]\
                        =np.log2(data_lbl.loc[:,('Ni%scut' % type_NorS)].astype('float'))
                        data_lbl.loc[(data_lbl.loc[:,('Ni%scutlog' % type_NorS)]==-np.inf) \
                                     | (data_lbl.loc[:,('Ni%scutlog' % type_NorS)]==np.inf),
                                     ('Ni%scutlog' % type_NorS)]=np.nan
                    
                    data_lbl.loc[:,'refi']=mutids_converter(data_lbl.loc[:,'mutids'],'refi',type_form)
                    data_lbl.loc[:,'ref']=mutids_converter(data_lbl.loc[:,'mutids'],'ref',type_form)
                    data_lbl.loc[:,'mut']=mutids_converter(data_lbl.loc[:,'mutids'],'mut',type_form)

                    sbam_fh=lbl_mat_mut_cds_fh.replace('.mat_mut_cds','')
                    if not exists(prj_dh+"/data_coverage"):
                        try:
                            makedirs(prj_dh+"/data_coverage")
                        except :
                            logging.warning("race error data_coverage")                    
                    if not exists(prj_dh+"/data_lbl/"+type_form):
                        try:
                            makedirs(prj_dh+"/data_lbl/"+type_form)
                        except :
                            logging.warning("race error data_lbl")
                    # get depth
                    if exists(sbam_fh):
                        depth_ref_fh="%s/data_coverage/%s.depth_ref" % (prj_dh,lbli)
                        depth_ref=getdepth_ref(sbam_fh,fsta_fh,cctmr=cctmr,data_out_fh=depth_ref_fh)
                        if 'refi' in depth_ref:
                            depth_ref=depth_ref.set_index('refi')
                        if 'refi' in data_lbl:
                            data_lbl=data_lbl.set_index('refi')
                        data_lbl=data_lbl.join(depth_ref)
                        data_lbl=data_lbl.reset_index()
                        data_lbl.loc[:,'NiA_norm']=data_lbl.loc[:,'NiAcut']/data_lbl.loc[:,'depth_ref']*data_lbl.loc[:,'depth_ref'].max()
                    else:
                        logging.info('no depth information')
                        data_lbl.loc[:,'NiA_norm']=data_lbl.loc[:,'NiAcut']
                    #clip ends
                    if not clips is None:
                        cols=[col for col in data_lbl.columns if not (('mut' in col) or ('ref' in col))]
                        # print cols
                        data_lbl.loc[(data_lbl.loc[:,'refi']<clips[0]),cols]=np.nan
                        data_lbl.loc[(data_lbl.loc[:,'refi']>clips[1]),cols]=np.nan
                    data_lbl.to_csv('%s/data_lbl/%s/%s' % (prj_dh,type_form,str(lbli)))
                else:
                    logging.error("len(data_lbl)/reflen is %d instead of 21 or 64" % (len(data_lbl)/(reflen/3)))
            else :
                logging.info("already processed: %s" % (str(lbli)))
        # if not exists(prj_dh+"/data_mutmat"):
        #     try:
        #         makedirs(prj_dh+"/data_mutmat")
        #     except :
        #         logging.warning("race error data_mutmat")
        # lbl_mat_cds_out_fh='%s/data_mutmat/%s' % (prj_dh,basename(lbl_mat_mut_cds_fh))
        # lbl_mat_cds.to_csv(lbl_mat_cds_out_fh)
    else :
        logging.warning("can not find lbl_mat_mut_cds_fh : %s" % (lbl_mat_mut_cds_fh))

def get_data_lbl_reps(data_lbl_fn,data_lbl_type,repli,info,data_fit=None,
                      data_lbl_col='NiA_tran',type_form='aas',col_sep='.'):
    if data_lbl_fn in repli.index:
        reps=repli.loc[data_lbl_fn,:].dropna()
        for rep in reps:
            data_lbl_fh="%s/data_lbl/%s/%s" % (info.prj_dh,type_form,rep)
            if exists(data_lbl_fh):
                data_lbl=pd.read_csv(data_lbl_fh)
                data_lbl=set_index(data_lbl,'mutids')

                data_fit_col="%s%s%s%s%s" % (rep,col_sep,data_lbl_col,col_sep,data_lbl_type)
                data_lbl_col="%s" % (data_lbl_col)
                if data_fit is None:
                    data_fit=data_lbl.loc[:,['ref','refi','mut']].copy()
                data_fit.loc[:,data_fit_col]=data_lbl.loc[:,data_lbl_col]
            else:
                logging.warning('%s does not exist' % basename(data_lbl_fh))
        if len(reps)==0:
            logging.warning("no replicates found in cfg: %s" % data_lbl_fn)
        else:
            return data_fit
    else:
        rep=data_lbl_fn
        data_lbl_fh="%s/data_lbl/%s/%s" % (info.prj_dh,type_form,rep)
        # print info.prj_dh
        if exists(data_lbl_fh):    
            data_lbl=pd.read_csv(data_lbl_fh).set_index('mutids')
            data_fit_col="%s%s%s%s%s" % (rep,col_sep,data_lbl_col,col_sep,data_lbl_type)
            data_lbl_col="%s" % (data_lbl_col)
            if data_fit is None:
                data_fit=data_lbl.loc[:,['ref','refi','mut']].copy()
            data_fit.loc[:,data_fit_col]=data_lbl.loc[:,data_lbl_col]
            return data_fit
        else:
            logging.warning('does not exists: %s' % data_lbl_fn)

def get_data_lbl_type(data_fit,data_lbl_type,data_lbl_col='NiA_tran'):
    data_lbl_type_col="%s.%s" % (data_lbl_col,data_lbl_type)
    data_lbl_type_reps_cols=[c for c in data_fit if data_lbl_type_col in c]
    # print data_lbl_type_reps_cols
    data_fit.loc[:,"%s avg" % (data_lbl_type_col)]=data_fit.loc[:,data_lbl_type_reps_cols].T.mean()
    data_fit.loc[:,"%s std" % (data_lbl_type_col)]=data_fit.loc[:,data_lbl_type_reps_cols].T.std()
    data_fit.loc[:,"%s" % (data_lbl_type_col)]=data_fit.loc[:,"%s avg" % (data_lbl_type_col)]
    
    return data_fit,data_lbl_type_reps_cols

#data_lbl_fn.NiA_trans.ref
def make_data_fit(data_lbl_ref_fn,data_lbl_sel_fn,info,data_lbl_col='NiA_tran',type_form='aas',
                 test='ztest',multitest='fdr_bh'):
    repli=pd.read_csv('%s/cfg/repli' % info.prj_dh).set_index('varname')
    col_sep="."
    data_fit=None
    data_lbl_type='ref'
    data_fit=get_data_lbl_reps(data_lbl_ref_fn,data_lbl_type,repli,info,data_fit=data_fit)
    if not data_fit is None:
        data_fit,data_lbl_ref_reps_cols=get_data_lbl_type(data_fit,data_lbl_type)
        data_lbl_type='sel'
        data_fit=get_data_lbl_reps(data_lbl_sel_fn,data_lbl_type,repli,info,data_fit=data_fit)
        if not data_fit is None:
            data_fit,data_lbl_sel_reps_cols=get_data_lbl_type(data_fit,data_lbl_type)            

            data_lbl_ref_col="%s.%s" % (data_lbl_col,'ref')
            data_lbl_sel_col="%s.%s" % (data_lbl_col,'sel')

            data_fit.loc[:,'FCA']=data_fit.loc[:,data_lbl_sel_col]-data_fit.loc[:,data_lbl_ref_col]
            data_fit.loc[:,'FCS']=data_fit.loc[(data_fit.loc[:,'mut']==data_fit.loc[:,'ref']),'FCA']
            #get zscores
            col_test_pval="pval %s" % test
            col_test_stat="stat %s" % test
            col_multitest_pval="padj %s %s" % (test,multitest)
            col_multitest_rjct="rejectH0 %s %s" % (test,multitest)
            #data_fit.to_csv('test.csv')# !!
            data_fit=testcomparison(data_fit,data_lbl_sel_reps_cols,data_lbl_ref_reps_cols,test=test)
            if not data_fit is None:
                if not sum(~pd.isnull(data_fit.loc[:,col_test_pval]))==0:
                    data_fit.loc[~pd.isnull(data_fit.loc[:,col_test_pval]),col_multitest_rjct],\
                    data_fit.loc[~pd.isnull(data_fit.loc[:,col_test_pval]),col_multitest_pval],a1,a2=\
                    multipletests(data_fit.loc[~pd.isnull(data_fit.loc[:,col_test_pval]),col_test_pval].as_matrix(),alpha=0.05, method=multitest)

                    data_fit.loc[:,'pval']=data_fit.loc[:,col_test_pval]
                    data_fit.loc[:,'stat']=data_fit.loc[:,col_test_stat]
                    data_fit.loc[:,'padj']=data_fit.loc[:,col_multitest_pval]    
                else:
                    data_fit.loc[:,'pval']=np.nan
                    data_fit.loc[:,'stat']=np.nan
                    data_fit.loc[:,'padj']=np.nan
                return data_fit

def make_deseq2_annot(unsel,sel,data_lbl_col,prj_dh,type_form='aas'):
    repli=pd.read_csv('%s/cfg/repli' % prj_dh).set_index('varname')
    col_sep="."
    data_deseq2_annot_dh='%s/data_fit/%s_all' % (prj_dh,type_form)
    data_deseq2_annot_fh='%s/%s_WRT_%s.deseq2_annot.csv' % (data_deseq2_annot_dh,sel,unsel)
    if not exists(data_deseq2_annot_fh):
        data_deseq2_annot=pd.DataFrame(columns=['condition','type','number of lanes',
                                                'total number of reads','exon counts'])
        data_deseq2_annot.index.name='file'
        if unsel in repli.index:
            for rep in repli.loc[unsel,:]:
                if not pd.isnull(rep):
                    data_deseq2_annot.loc["%s%s%s" % (rep,col_sep,data_lbl_col),'condition']='ref'
        else:
            data_deseq2_annot.loc["%s%s%s" % (unsel,col_sep,data_lbl_col),'condition']='ref'
            
        if sel in repli.index:
            for rep in repli.loc[sel,:]:
                if not pd.isnull(rep):
                    data_deseq2_annot.loc["%s%s%s" % (rep,col_sep,data_lbl_col),'condition']='sel'
        else:
            data_deseq2_annot.loc["%s%s%s" % (sel,col_sep,data_lbl_col),'condition']='sel'

        if not exists(data_deseq2_annot_dh):
            try:
                makedirs(data_deseq2_annot_dh)
            except:
                logging.info("race error /data_fit/")
        data_deseq2_annot.to_csv(data_deseq2_annot_fh)
    else:
        data_deseq2_annot=pd.read_csv(data_deseq2_annot_fh).set_index('file')
    return data_deseq2_annot,data_deseq2_annot_fh

def make_deseq2_count(unsel,sel,data_deseq2_annot,data_lbl_col,prj_dh,type_form='aas'):
    data_deseq2_count_dh='%s/data_fit/%s_all' % (prj_dh,type_form)
    data_deseq2_count_fh='%s/%s_WRT_%s.deseq2_count.csv' % (data_deseq2_count_dh,sel,unsel)
    if not exists(data_deseq2_count_fh):
        data_lbl_fhs=["%s/data_lbl/%s/%s" % (prj_dh,type_form,s.split('.')[0]) for s in data_deseq2_annot.index]
        col_sep="."
        data_lbl_all=fhs2data_combo(data_lbl_fhs,cols=[data_lbl_col],index='mutids',col_sep=col_sep)
        data_lbl_all=debad(data_lbl_all,axis=0,condi='any',bad='nan')
        data_lbl_all.to_csv(data_deseq2_count_fh)
    else:
        data_lbl_all=pd.read_csv(data_deseq2_count_fh).set_index('mutids')
    return data_lbl_all,data_deseq2_count_fh

def make_GLM_norm(data_lbl_ref_fn,data_lbl_sel_fn,data_fit,info):
    data_lbl_col='NiA_norm'
    data_deseq2_annot,data_deseq2_annot_fh=make_deseq2_annot(data_lbl_ref_fn,data_lbl_sel_fn,
                                                             data_lbl_col,info.prj_dh)
    data_deseq2_count,data_deseq2_count_fh=make_deseq2_count(data_lbl_ref_fn,data_lbl_sel_fn,
                                                             data_deseq2_annot,data_lbl_col,info.prj_dh)
    data_deseq2_count=set_index(data_deseq2_count,'mutids')
    if len(data_deseq2_count.columns)==2:
        logging.error('transform_type can not be GLM: no replicates found')
        sys.exit()
    log_fh="%s.log" % data_deseq2_annot_fh
    data_deseq2_res_fh="%s.deseq2_res.csv" % data_deseq2_annot_fh
    if not exists(data_deseq2_res_fh):
        deseq_fh="%s/deseq2.R" % (abspath(dirname(__file__)))
        with open(log_fh,'a') as log_f:
            com='%s %s %s %s 2' % (info.rscript_fh,deseq_fh,data_deseq2_count_fh,data_deseq2_annot_fh)
#             print com
            subprocess.call(com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)  
    try:
        data_deseq2_res=pd.read_csv(data_deseq2_res_fh).set_index('Unnamed: 0')
    except:
        logging.error('check deseq2 log for more info: %s' % basename(log_fh))
        logging.error("check if deseq2 is installed.")
    data_deseq2_res.index.name='mutids'
#     baseMean  log2FoldChange  lfcSE   stat    pvalue  padj
    test='Waldtest'
    multitest='fdr_bh'              
    col_test_pval="pval %s" % test
    col_test_stat="stat %s" % test
    col_multitest_pval="padj %s %s" % (test,multitest)

    cols=data_deseq2_res.columns.tolist()
    cols=[col_test_pval if s=='pvalue' else s for s in cols]
    cols=[col_test_stat if s=='stat' else s for s in cols]
    cols=[col_multitest_pval if s=='padj' else s for s in cols]
    data_deseq2_res.columns=cols

    data_deseq2_res.loc[:,'pval']=data_deseq2_res.loc[:,col_test_pval]
    data_deseq2_res.loc[:,'stat']=data_deseq2_res.loc[:,col_test_stat]
    data_deseq2_res.loc[:,'padj']=data_deseq2_res.loc[:,col_multitest_pval]    

    data_deseq2_res.loc[:,'FCA_norm']=data_deseq2_res.loc[:,'log2FoldChange']
    #set wald as default stat
    data_fit=data_fit.drop(['pval','stat','padj'],axis=1)
    data_fit=data_fit.join(data_deseq2_res)
    return data_fit

from dms2dfe.lib.io_mut_class import class_fit
def data_lbl2data_fit(data_lbl_ref_fn,data_lbl_sel_fn,info,type_forms=['aas']):
    for type_form in type_forms : # cds OR aas
        data_fit_fh='%s/data_fit/%s/%s_WRT_%s' % (info.prj_dh,type_form,data_lbl_sel_fn,data_lbl_ref_fn)
        if not exists(data_fit_fh):
            data_fit=make_data_fit(data_lbl_ref_fn,data_lbl_sel_fn,info,data_lbl_col='NiA_tran',type_form='aas')
            if not data_fit is None:
                if info.norm_type=='GLM':
                    data_fit=make_GLM_norm(data_lbl_ref_fn,data_lbl_sel_fn,data_fit,info)
                elif (info.norm_type=='MLE') or (info.norm_type=='syn'):
                    try:
                        gauss_mean, gauss_sdev = fit_gauss_params(data_fit.loc[:,'FCS'])
                        data_fit.loc[:,'FCA_norm']=(data_fit.loc[:,'FCA']-gauss_mean)/gauss_sdev
                    except:
                        logging.error("norm wrt syn: excepted: data_fit/%s/%s" % (type_form,basename(data_fit_fh)))
                        sys.exit()
                elif info.norm_type == 'none':
                    data_fit.loc[:,'FCA_norm']=data_fit.loc[:,'FCA']
                data_fit.loc[:,'FCS_norm']=data_fit.loc[(data_fit.loc[:,'mut']==data_fit.loc[:,'ref']),'FCA_norm']
                if hasattr(info, 'rescaling'):
                    if info.rescaling=='TRUE':
                        data_fit=rescale_fitnessbysynonymous(data_fit,col_fit="FCA_norm",col_fit_rescaled="FiA")
                    else:
                        data_fit.loc[:,'FiA']=data_fit.loc[:,'FCA_norm']           
                else:
                    data_fit.loc[:,'FiA']=data_fit.loc[:,'FCA_norm']
                if hasattr(info, 'mut_subset'):
                    if info.mut_subset=='N':
                        data_fit.loc[(data_fit.loc[:,'mut']==data_fit.loc[:,'ref']),'FiA']=np.nan
                    elif info.mut_subset=='S':
                        data_fit.loc[(data_fit.loc[:,'mut']!=data_fit.loc[:,'ref']),'FiA']=np.nan
                else:
                    data_fit.loc[(data_fit.loc[:,'mut']==data_fit.loc[:,'ref']),'FiA']=np.nan                                
                data_fit=class_fit(data_fit,col_fit="FiA")
                if not exists(dirname(data_fit_fh)):
                    try:
                        makedirs(dirname(data_fit_fh))
                    except:
                        logging.info("race error /data_fit/")
                data_fit.to_csv(data_fit_fh)

def rescale_fitnessbysynonymous(data_fit,col_fit="FCA_norm",col_fit_rescaled="FiA",syn2nan=True):
    if not sum(~pd.isnull(data_fit.loc[(data_fit.loc[:,'mut']==data_fit.loc[:,'ref']),col_fit]))==0:
        data_fit=set_index(data_fit,'mutids')
        if col_fit_rescaled in data_fit.columns:
            col_fit_rescaled_ori=col_fit_rescaled
            col_fit_rescaled    ="tmp"
        if not "refrefi" in data_fit:
            data_fit.loc[:,'refrefi']\
            =mutids_converter(data_fit.reset_index().loc[:,'mutids'],
                              'refrefi','aas')        
        for refrefi in data_fit.loc[:,"refrefi"].unique():
            data_fit_posi=data_fit.loc[data_fit.loc[:,"refrefi"]==refrefi,:]
            FiS=float(data_fit_posi.loc[data_fit_posi.loc[:,"mut"]==data_fit_posi.loc[:,"ref"],col_fit])
            for mutid in data_fit_posi.index:
                data_fit.loc[mutid,col_fit_rescaled]=data_fit.loc[mutid,col_fit]-FiS
        if "tmp" in data_fit.columns:
            data_fit.loc[:,col_fit_rescaled_ori]=data_fit.loc[:,"tmp"]
            data_fit=data_fit.drop("tmp",axis=1)
        if syn2nan:
            data_fit.loc[(data_fit.loc[:,'ref']==data_fit.loc[:,'mut']),col_fit_rescaled]=np.nan
        return data_fit
    else:
        logging.info('no synonymous mutations available')
        data_fit.loc[:,col_fit_rescaled]=np.nan
        # data_fit.loc[:,col_fit_rescaled]
        return data_fit

def data_lbl2data_fit_lite(fits_pairs,prj_dh,data_lbl_dh,data_fit_dh,force=False):
    data_fit_fh='%s/%s/aas/%s_WRT_%s' % (prj_dh,data_fit_dh,fits_pairs[1],fits_pairs[0])
    if not exists(data_fit_fh) or force:
        data_lbl_fhs=['%s/%s/aas/%s' % (prj_dh,data_lbl_dh,s) for s in fits_pairs]

        data_fit=fhs2data_combo(data_lbl_fhs,cols=['NiA_tran'],
        #                labels=['ref','sel'],
                       index='mutids',col_sep='.')
        data_fit.columns=['NiA_tran.ref','NiA_tran.sel']
        data_fit.loc[:,'FCA']=data_fit.loc[:,'NiA_tran.sel']-data_fit.loc[:,'NiA_tran.ref']
        data_fit.loc[:,'FCA_norm']=data_fit.loc[:,'NiA_tran.sel']-data_fit.loc[:,'NiA_tran.ref']
        if not exists(dirname(data_fit_fh)):
            makedirs(dirname(data_fit_fh))
        data_fit.to_csv(data_fit_fh)
        
from dms2dfe.lib.io_mut_class import class_comparison
def data_fit2data_comparison(lbl_ctrl,lbl_test,prj_dh):
    """
    This converts the Fitness values to Relative fitness among test and control fed as input.
    
    .. code-block:: text
    
        class fit:           beneficial, neutral, deleterious
        class comparison:    killed, survived
        class comparison:    positive, negative, robust
        
    :param lbl_ctrl: name of control sample.
    :param lbl_test: name of test sample.
    :param prj_dh: path to project directory.
    """    
    logging.info("processing: ctrl, test : %s %s" % (lbl_ctrl,lbl_test))
    for type_form in ['aas']:#stitch mut_types_form : # get aas or cds
        data_fit_ctrl_fhs=glob("%s/data_fit/%s/%s_WRT*" % (prj_dh,type_form,lbl_ctrl))
        data_fit_ctrl_keys=[basename(fh) for fh in data_fit_ctrl_fhs]
        data_fit_test_fhs=glob("%s/data_fit/%s/%s_WRT*" % (prj_dh,type_form,lbl_test))
        data_fit_test_keys=[basename(fh) for fh in data_fit_test_fhs]
        if (data_fit_ctrl_keys and data_fit_test_keys):
            for ctrli in data_fit_ctrl_keys :
                for testi in data_fit_test_keys :       
                    data_comparison_fh='%s/data_comparison/%s/%s_VERSUS_%s' % (prj_dh,type_form,testi,ctrli)
                    if not exists(data_comparison_fh):
                        if not "inferred" in data_comparison_fh:
                            # print data_comparison_fh
                            # if 'inferred' in data_comparison_fh:
                            #     print ">>>>%s" % data_comparison_fh
                            data_fit_ctrl_fh="%s/data_fit/%s/%s" % (prj_dh,type_form,ctrli)
                            data_fit_ctrl=pd.read_csv(data_fit_ctrl_fh)
                            data_fit_test_fh="%s/data_fit/%s/%s" % (prj_dh,type_form,testi)
                            data_fit_test=pd.read_csv(data_fit_test_fh)
                            # print data_fit_test_fh
                            # df1,df2,idx_col,df1_cols,df2_cols,
                            # df1_suffix,df2_suffix
                            data_comparison=concat_cols(df1=data_fit_test,df2=data_fit_ctrl,
                                                        idx_col='mutids',
                                    df1_cols=['mut','ref','FiA',"class_fit",'padj'],
                                    df2_cols=['FiA',"class_fit",'padj'],
                                    df1_suffix='_test',df2_suffix='_ctrl',
                                    wc_cols=['.NiA_tran.ref','.NiA_tran.sel'],
                                                       suffix_all=True)

                            data_comparison.loc[:,"Fi_ctrl"]=data_comparison.loc[:,"FiA_ctrl"]
                            data_comparison.loc[:,"Fi_test"]=data_comparison.loc[:,"FiA_test"]
                            data_comparison.loc[((data_comparison.loc[:,"padj_ctrl"]<0.05) \
                             & (data_comparison.loc[:,"padj_test"]<0.05)),'Significant']=True
                            data_comparison.loc[pd.isnull(data_comparison.loc[:,'Significant']),'Significant']=False
        #                     data_comparison.to_csv("test_comparison")
                            # data_comparison=class_comparison(data_comparison) # get class fit rel
                            data_comparison.loc[:,'class_comparison']=class_comparison(data_fit_test,data_fit_ctrl)
                            if not exists('%s/data_comparison/%s' % (prj_dh,type_form)):
                                try:
                                    makedirs('%s/data_comparison/%s' % (prj_dh,type_form))
                                except:
                                    logging.info("race error data_comparison")
                            data_comparison.reset_index().to_csv(data_comparison_fh,index=False) # store                    
        else:
            logging.warning("do not exist: data_fit/%s/%s & data_fit/%s/%s" % (type_form,lbl_ctrl,type_form,lbl_test))
