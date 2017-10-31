# Copyright 2017, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
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

from dms2dfe.lib.io_dfs import set_index

def getcolsmets(d,cs):
    cols=[c for c in d.columns if cs in c]
    counts=[len(d[c].dropna()) for c in cols]
    return dict(zip(cols,counts))

def get_2SD_cutoffs(d,reps,N=False):
    t=d.copy()
    mus=[]
    sigmas=[]
    for r1i,r1 in enumerate(reps):
        for r2i,r2 in enumerate(reps):
            if r1i<r2i:
                t.loc[:,'reps']=t.loc[:,r1]-t.loc[:,r2]
                if N and ('mut' in t):
                    t.loc[(t.loc[:,'mut']==t.loc[:,'ref']),'reps']=np.nan
                mus.append(t.loc[:,'reps'].mean())
                sigmas.append(t.loc[:,'reps'].std())                
    mu=np.mean(mus)
    sigma=np.sqrt(np.mean([s**2 for s in sigmas]))
    return mu+sigma*2,mu,sigma

def get_repli_FiA(d,csel='.NiA_tran.sel',cref='.NiA_tran.ref'):
    sels=np.sort([c for c in d.columns if csel in c])
    refs=np.sort([c for c in d.columns if cref in c])
    FCAi=1
    cols_FCA=[]
    for refi,ref in enumerate(refs):
        for seli,sel in enumerate(sels):
            if refi==seli:
                coln='FCA%s_reps' % FCAi
                d.loc[:,coln]=d.loc[:,sel]-d.loc[:,ref]
                d.loc[(d.loc[:,'mut']==d.loc[:,'ref']),coln]=np.nan
                cols_FCA.append(coln)
                FCAi+=1
    return d.loc[:,cols_FCA]

def data_fit2cutoffs(d,sA,sB,N=True):
    refs=[c for c in d.columns if sA in c]
    sels=[c for c in d.columns if sB in c]
    _,mu1,sigma1=get_2SD_cutoffs(d,refs)
    _,mu2,sigma2=get_2SD_cutoffs(d,sels)
    return np.mean([mu1,mu2])+2*np.sqrt(np.mean([sigma1,sigma2]))

def class_fit(d,col_fit='FiA',FC=True,zscore=False): #column of the data_fit
    """
    This classifies the fitness of mutants into beneficial, neutral or, deleterious.
    
    :param d: dataframe of `data_fit`.
    :returns d: classes of fitness written in 'class-fit' column based on values in column 'FiA'. 
    """
    cols_reps=[c for c in d if '.NiA_tran.ref' in c]
    if FC and (len(cols_reps)==2):
        up,_,_=get_2SD_cutoffs(d,cols_reps,N=True)
        dw=-1*up
    else:
        if zscore:
            up,dw=-2,2
        else:
            up,dw=0,0
    d.loc[d.loc[:,col_fit]>+up,    'class_fit']="enriched"
    d.loc[((d.loc[:,col_fit]>=dw) & (d.loc[:,col_fit]<=up)),'class_fit']="neutral"
    d.loc[d.loc[:,col_fit]<dw,    'class_fit']="depleted"
    return d

def class_comparison(dA,dB):
    """
    This classifies differences in fitness i.e. relative fitness into positive, negative or robust categories. 
    
    :param dc: dataframe with `dc`. 
    :returns dc: dataframe with `class__comparison` added according to fitness levels in input and selected samples in `dc`
    """
    dA=set_index(dA,'mutids')
    dB=set_index(dB,'mutids')
    dc=get_repli_FiA(dA).join(get_repli_FiA(dB),lsuffix='_test',rsuffix='_ctrl')
    up=data_fit2cutoffs(dc,sA='_reps_test',sB='_reps_ctrl',N=False)
    dw=-1*up

    diff=dA.loc[:,'FiA']-dB.loc[:,'FiA']
    diff.index.name='mutids'
    diff=diff.reset_index()
    mutids_up=diff.loc[(diff.loc[:,'FiA']>up),'mutids'].tolist()
    mutids_dw=diff.loc[(diff.loc[:,'FiA']<dw),'mutids'].tolist()

    dc.loc[mutids_up,'class_comparison']="positive"
    dc.loc[mutids_dw,'class_comparison']="negative"
    return dc.loc[:,'class_comparison']


def get_data_metrics(prj_dh):
    data_fit_fns_all=[basename(s) for s in glob('%s/data_fit/aas/*' % prj_dh)]
    data_fit_fns_all2labels=dict(zip(data_fit_fns_all,data_fit_fns_all))
    data_fit_metrics=pd.DataFrame(index=data_fit_fns_all)

    fit=pd.read_csv('%s/cfg/fit' % prj_dh).set_index('unsel')
    comparison=pd.read_csv('%s/cfg/comparison' % prj_dh).set_index('ctrl')

    for ctrl in comparison.index:
        fh_ctrls=glob('%s/data_fit/aas/%s_WRT_*' % (prj_dh,ctrl))
        for fh_ctrl in fh_ctrls:
            dctrl=pd.read_csv(fh_ctrl).set_index('mutids')

            up,_,_=get_2SD_cutoffs(dctrl,[c for c in dctrl if '.NiA_tran.ref' in c],N=True)
            dw=-1*up
            # print up,dw
            ctrl=basename(fh_ctrl)
            ctrls={'versus_%s' % ctrl:ctrl}

            data_fit_metrics.index.name='fn'
            for fni,fn in enumerate(data_fit_fns_all):
                fh= '%s/data_fit/aas/%s' % (prj_dh,fn)
                d=pd.read_csv(fh).set_index('mutids')
                data_fit_metrics.loc[fn,'$\mu+2\sigma$']=up
                d=d.reset_index()
                mutids_up=d.loc[(d.loc[:,'FiA']>up),'mutids'].tolist()
                mutids_dw=d.loc[(d.loc[:,'FiA']<dw),'mutids'].tolist()
                mutids_updw=mutids_up+mutids_dw
                d=d.set_index('mutids')
                data_fit_metrics.loc[fn,'$n$']=len(d.loc[:,'FiA'].dropna())
                ref_counts=getcolsmets(d,cs='.NiA_tran.ref')
                sel_counts=getcolsmets(d,cs='.NiA_tran.sel')
                for i,_ in enumerate(ref_counts.keys()):
                    data_fit_metrics.loc[fn,'$n$ ref%02d' % i]=ref_counts[ref_counts.keys()[i]]
                for i,_ in enumerate(sel_counts.keys()):
                    data_fit_metrics.loc[fn,'$n$ sel%02d' % i]=sel_counts[sel_counts.keys()[i]]
                data_fit_metrics.loc[fn,'$n_{neutral}$']=data_fit_metrics.loc[fn,'$n$']-len(mutids_updw)
                data_fit_metrics.loc[fn,'$n_{enriched}$']=len(mutids_up)
                data_fit_metrics.loc[fn,'$n_{depleted}$']=len(mutids_dw)
                data_fit_metrics.loc[fn,'$F$ mean']=d.loc[:,'FiA'].mean()
    
    if len(data_fit_metrics.columns)>0:
        data_fit_metrics['$n_{enriched}$%%']=data_fit_metrics['$n_{enriched}$']\
        /(data_fit_metrics['$n_{enriched}$']+data_fit_metrics['$n_{depleted}$'])*100
        data_fit_metrics['$n_{depleted}$%%']=data_fit_metrics['$n_{depleted}$']\
        /(data_fit_metrics['$n_{enriched}$']+data_fit_metrics['$n_{depleted}$'])*100
        data_fit_metrics['$n_{enriched}$%']=data_fit_metrics['$n_{enriched}$']/data_fit_metrics['$n$']*100
        data_fit_metrics['$n_{depleted}$%']=data_fit_metrics['$n_{depleted}$']/data_fit_metrics['$n$']*100
        data_fit_metrics['$n_{neutral}$%']=data_fit_metrics['$n_{neutral}$']/data_fit_metrics['$n$']*100

        data_fit_metrics['$E$']=data_fit_metrics['$n_{enriched}$']/\
        (data_fit_metrics['$n_{enriched}$']+data_fit_metrics['$n_{depleted}$'])
        # print data_fit_metrics.index
        # print data_fit_metrics.columns
        
        data_fit_metrics.loc[:,'labels']=[data_fit_fns_all2labels[i] for i in data_fit_metrics.index]

        for c in ctrls:
            fh= '%s/data_fit/aas/%s' % (prj_dh,ctrls[c])
            dA=pd.read_csv(fh).set_index('mutids')
            for fni,fn in enumerate(data_fit_fns_all):
                fh= '%s/data_fit/aas/%s' % (prj_dh,fn)
                dB=pd.read_csv(fh).set_index('mutids')            
                dc=get_repli_FiA(dA).join(get_repli_FiA(dB),lsuffix='_ctrl',rsuffix='_test')
                up=data_fit2cutoffs(dc,sA='_reps_test',sB='_reps_ctrl',N=False)
                dw=-1*up
                data_fit_metrics.loc[fn,'$\mu+2\sigma$ comparison %s' % c]=up

                diff=dB.loc[:,'FiA']-dA.loc[:,'FiA']
                diff=diff.reset_index()
                mutids_up=diff.loc[(diff.loc[:,'FiA']>up),'mutids'].tolist()
                mutids_dw=diff.loc[(diff.loc[:,'FiA']<dw),'mutids'].tolist()
                mutids_updw=mutids_up+mutids_dw
                diff=diff.set_index('mutids')
                data_fit_metrics.loc[fn,'$n$ %s' % c]=len(diff.dropna())
                data_fit_metrics.loc[fn,'$n_{positive}$ %s' % c]=len(mutids_up)
                data_fit_metrics.loc[fn,'$n_{negative}$ %s' % c]=len(mutids_dw)

            data_fit_metrics['$\Delta n$ %s' % c]=(data_fit_metrics['$n$']-data_fit_metrics.loc[ctrls[c],'$n$'])
            data_fit_metrics['$\Delta n_{enriched}$ %s' % c]=(data_fit_metrics['$n_{enriched}$']-data_fit_metrics.loc[ctrls[c],'$n_{enriched}$'])
            data_fit_metrics['$\Delta n_{enriched}$%% %s' % c]=(data_fit_metrics['$n_{enriched}$%']-data_fit_metrics.loc[ctrls[c],'$n_{enriched}$%'])
            data_fit_metrics['$\Delta F$ %s' % c]=(data_fit_metrics['$F$ mean']-data_fit_metrics.loc[ctrls[c],'$F$ mean'])
        data_fit_metrics_fh='%s/data_comparison/data_fit_metrics' % prj_dh
        data_fit_metrics.to_csv(data_fit_metrics_fh)
        return data_fit_metrics
    else: 
        logging.info('data_metrics has 0 cols')