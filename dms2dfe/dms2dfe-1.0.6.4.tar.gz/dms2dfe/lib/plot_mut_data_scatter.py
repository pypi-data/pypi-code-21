#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

"""
================================
``plot``
================================
"""
import sys
from os.path import splitext,exists,basename
from os import makedirs,stat
import pandas as pd
import numpy as np
import matplotlib
matplotlib.style.use('ggplot')
matplotlib.rcParams['axes.unicode_minus']=False
matplotlib.use('Agg') # no Xwindows
import matplotlib.pyplot as plt
# matplotlib.style.use('ggplot')
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # 

# from dms2dfe.lib.io_strs import make_pathable_string
from dms2dfe.lib.io_plots import saveplot,get_axlims
from dms2dfe.lib.io_dfs import set_index,denanrows


def gettopnlastdiff(data,col1,col2,zcol=None,rows=5,zcol_threshold=None,
                    col_classes=None,classes=[]):
    data.loc[:,'diff']=data.loc[:,col2]-data.loc[:,col1]
    if zcol is None:
        data_heads=data.sort_values(by='diff',ascending=True).head(rows)#.index
        data_tails=data.sort_values(by='diff',ascending=True).tail(rows)#.index
    else:
        if not zcol_threshold is None:
            data=data.loc[(data.loc[:,zcol]<zcol_threshold),:]
        # df.sort_values(['a', 'b'], ascending=[True, False])
        data_heads=data.sort_values(by=['diff',zcol],ascending=[True,True]).head(rows)#.index
        data_tails=data.sort_values(by=['diff',zcol],ascending=[True,False]).tail(rows)#.index
    if not col_classes is None:
        data_heads=data_heads.loc[(data_heads.loc[:,col_classes]==classes[0]),:]
        data_tails=data_tails.loc[(data_tails.loc[:,col_classes]==classes[1]),:]        
    return data_heads.index,data_tails.index,

from dms2dfe.lib.plot_mut_data import data2mut_matrix,data2sub_matrix
# from dms2dfe.lib.io_mut_files import concat_cols
from dms2dfe.lib.io_plots import repel_labels
def plot_sc(data,ax,xcol,ycol,ylabel='',
           heads=[],tails=[],repel=0.045,
           annot_headtails=True,
            color_sca=None,
            color_dots='both',
            color_heads='r',color_tails='b',
            zcol=None,
            zcol_threshold=None,
            diagonal=True,
            space=0.2,
            axlims=None,
           ):
    if (not zcol is None) and (sum(~pd.isnull(data.loc[:,zcol]))==0):
        zcol=None
    if zcol is None:
        ax=data.plot.scatter(xcol,ycol,edgecolor='none',alpha=0.6,
                             c='yellowgreen',
                             ax=ax)
    else:
        data=data.sort_values(by=zcol,ascending=False)
        ax.scatter(x=data.loc[:,xcol],
                   y=data.loc[:,ycol],
                   edgecolor='none',
                   alpha=0.6,
                   c=data.loc[:,zcol],
                  cmap='summer_r',
                  )
        ax.set_xlabel(xcol)
    if len(heads)==0 and len(tails)==0:
        if annot_headtails:
            heads,tails=gettopnlastdiff(data,ycol,xcol,zcol=zcol,zcol_threshold=zcol_threshold)
    color_sca='none'
    color_edge='royalblue'
    if (color_dots=='heads') or (color_dots=='both'):
        ax.scatter(x=data.loc[heads,xcol],y=data.loc[heads,ycol],
                                          edgecolor=color_edge,
                                          facecolors=color_sca,
                                         )
        try:
            repel_labels(ax, data.loc[heads, xcol], data.loc[heads, ycol], heads, k=repel,label_color=color_heads)
        except:
            for s in heads:
                ax.text(data.loc[s, xcol], data.loc[s, ycol], s,color=color_heads)    
    if (color_dots=='tails') or (color_dots=='both'):
        ax.scatter(x=data.loc[tails,xcol],y=data.loc[tails,ycol],
                                          edgecolor=color_edge,
                                          facecolors=color_sca,
                                          )    
        try:
            repel_labels(ax, data.loc[tails, xcol], data.loc[tails, ycol], tails, k=repel,label_color=color_tails)
        except:
            for s in tails:
                if s in data.index:
                    ax.text(data.loc[s, xcol], data.loc[s, ycol], s,color=color_tails)
    ax.set_ylabel(ylabel)
    if diagonal:
        ax.plot([100,-100],[100,-100],linestyle='-',color='darkgray',zorder=0)
    if axlims is None:
        xlims,ylims=get_axlims(data.loc[:,xcol],data.loc[:,ycol],space=space)
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
        axlims=[xlims,ylims]
    else:
        ax.set_xlim(axlims[0])
        ax.set_ylim(axlims[1])  
    return ax,heads,tails,axlims

def mutids2refrei(mutid):
    return mutid[:-1]
def mutids2subid(mutid):
    return mutid[0]+mutid[-1]

def plot_scatter_mutilayered(data_all,xcol,ycol,
                             mutids_heads=[],mutids_tails=[],
                             repel=0.045,
                             color_dots='both',
                             annot_headtails=True,
                             color_heads='r',color_tails='b',
                             note_text='',                             
                             stds_sub_pos=None,
                             col_z_mutations=None,
                             zcol_threshold=None,
                             errorbars=False,
                             diagonal=True,
                             space=0.2,
                             figsize=[8.5,6],
                             plot_fh=None,):
    # print data_all.shape    
    if 'mutids' in data_all:
        data_all=data_all.set_index('mutids')
    data_all_mut=data_all.copy()
    if not col_z_mutations is None:
        data_all=data_all.drop(col_z_mutations,axis=1)
    # sum(~pd.isnull(data_all_mut.loc[:,col_z_mutations]))
    data_all_pos=pd.concat([data2mut_matrix(data_all.reset_index(),xcol,'mut','aas').mean(),
                            data2mut_matrix(data_all.reset_index(),ycol,'mut','aas').mean(),
                            data2mut_matrix(data_all.reset_index(),xcol,'mut','aas').std(),
                            data2mut_matrix(data_all.reset_index(),ycol,'mut','aas').std(),
                           ],axis=1)
    data_all_pos.columns=[xcol,ycol,xcol+'std',ycol+'std']
    data_all_sub=pd.concat([data2sub_matrix(data_all,xcol,'mut','aas',aggfunc='mean').unstack(),
                            data2sub_matrix(data_all,ycol,'mut','aas',aggfunc='mean').unstack(),
                            data2sub_matrix(data_all,xcol,'mut','aas',aggfunc='std').unstack(),
                            data2sub_matrix(data_all,ycol,'mut','aas',aggfunc='std').unstack(),
                           ],axis=1)
    data_all_sub.columns=[xcol,ycol,xcol+'std',ycol+'std']
    data_all_sub=denanrows(data_all_sub)
    if not 'Wild type' in data_all_sub:
        data_all_sub=data_all_sub.reset_index()
    mutids=[]
    for i in data_all_sub.index:
        mutids.append('%s%s' % (data_all_sub.reset_index().loc[i,'Wild type'],
                                  data_all_sub.reset_index().loc[i,'Mutation to']))
    data_all_sub.loc[:,'mutids']=mutids
    data_all_sub=data_all_sub.set_index('mutids')

    fig=plt.figure(figsize=figsize)
    ax1=plt.subplot(131)
    ax2=plt.subplot(132)
    ax3=plt.subplot(133)
    if errorbars:
        ax2.errorbar(data_all_sub.loc[:,xcol],data_all_sub.loc[:,ycol],
                     xerr=data_all_sub.loc[:,xcol+'std'],
                     yerr=data_all_sub.loc[:,ycol+'std'],
                     fmt="none",ecolor='gray',alpha=0.15, 
                     capthick=0,
                     zorder=0)
        ax3.errorbar(data_all_pos.loc[:,xcol],data_all_pos.loc[:,ycol],
                     xerr=data_all_pos.loc[:,xcol+'std'],
                     yerr=data_all_pos.loc[:,ycol+'std'],
                     fmt="none",ecolor='gray',alpha=0.15, 
                     capthick=0,
                     zorder=0)
    ax1,mutids_heads,mutids_tails,axlims=plot_sc(data_all_mut,ax1,xcol,ycol,ylabel=ycol,
                heads=mutids_heads,tails=mutids_tails,
                annot_headtails=False,
                zcol=col_z_mutations,zcol_threshold=zcol_threshold,
                repel=repel,
                color_dots=color_dots,color_heads=color_heads,color_tails=color_tails,diagonal=diagonal,space=space,)

    repel_sub=repel*len(data_all_sub)/(len(data_all_mut))*5
    if repel_sub>repel:
        repel_sub=repel
    # print repel_sub
    # print data_all_sub.columns
    # data_all_sub=denanrows(data_all_sub)
    data_all_sub=data_all_sub.loc[denanrows(data_all_sub.loc[:,[xcol,ycol]]).index.tolist(),:]
    # print data_all_sub.shape
    ax2,_,_,_=plot_sc(data_all_sub,ax2,xcol,ycol,
               heads=[mutids2subid(i) for i in mutids_heads],tails=[mutids2subid(i) for i in mutids_tails],
                annot_headtails=False,
               repel=repel_sub,
                color_dots=color_dots,color_heads=color_heads,color_tails=color_tails,diagonal=diagonal,space=space,
                     # axlims=axlims
                     )
    repel_pos=repel*len(data_all_pos)/(len(data_all_mut))*12.5
    if repel_pos>repel:
        repel_pos=repel
    # print repel_pos
    ax3,_,_,_=plot_sc(data_all_pos,ax3,xcol,ycol,
               heads=[mutids2refrei(i) for i in mutids_heads],tails=[mutids2refrei(i) for i in mutids_tails],
                annot_headtails=False,
               repel=repel_pos,
                color_dots=color_dots,color_heads=color_heads,color_tails=color_tails,diagonal=diagonal,space=space,
                     # axlims=axlims
                     )
    ax1.set_title('Mutations',color="gray")
    ax2.set_title('Substitutions',color="gray")
    ax3.set_title('Positions',color="gray")
    fig.suptitle(note_text, fontsize=15,color="k")
    saveplot(plot_fh,form='both',transparent=False)    
    return data_all_mut,data_all_sub,data_all_pos

def set_title_higher(axes,labels,height=1.2,color='k'):
    for i in range(len(labels)):
        ax=axes[i]
        label=labels[i]
        x=ax.get_xlim()[0]
        y=ax.get_ylim()[0]+(ax.get_ylim()[1]-ax.get_ylim()[0])*height
        ax.text(x,y,label,
                color=color,fontsize=15)
        

def data_comparison2scatter_mutilayered(data,data_label,color_dots=None,
                                         mutids_heads=[],mutids_tails=[],
                                        col_filter=None,
                                        note_text=None,
                                        col_pvals=None,
                                        repel=0.045,
                                        figsize=[15,5],
                                        plot_fh=None):
    from dms2dfe.lib.io_strs import splitlabel

    # print data.shape
    data=set_index(data,'mutids')
    labels=splitlabel(data_label,splitby=' versus ',ctrl='$37^{0}$C')
    if not note_text is None:
        labels=["%s (%s)" % (l,note_text) for l in labels] 
    data.loc[:,labels[0]]=data.loc[:,'Fi_test']
    data.loc[:,labels[1]]=data.loc[:,'Fi_ctrl']
    if not col_pvals is None:
        data.loc[:,col_pvals]=np.log10(data.loc[:,col_pvals])
        if not data.index.name=='mutids':
            data.index.name='mutids'
#         print data.index
        zcol_threshold=np.log10(0.01)
    if not col_filter is None:
        data.loc[data.loc[:,col_filter],labels]
    cols=['mut','ref']+labels
    if not col_pvals is None:
        cols=cols+[col_pvals]
    data=denanrows(data.loc[:,cols])
    # print data.shape
    # print data.index.name
    # print data.columns.tolist()

    plot_scatter_mutilayered(data,labels[1],labels[0],
                             plot_fh=plot_fh,
                            color_dots=color_dots,
                             mutids_heads=mutids_heads,
                             mutids_tails=mutids_tails,
                             color_heads='b',color_tails='b',
                             col_z_mutations=col_pvals,
                             zcol_threshold=0.05,
                             repel=repel,
                             figsize=figsize,#[6.375,4.5],
                            )

def plot_mulitilayered_scatter_per_class_comparison(prj_dh,
                                                    data_fns,data_labels,
                                                    filter_selection=None,
                                                    data_sections_pvals=None,
                                                    fns2sides=None,
                                                    filter_sections=None,
                                                    filter_signi=True,
                                                    col_pvals=None,
                                                    col_filter=None,
                                                    figsize=[9,3],
                                                    force=False):
    plot_type='scatter_mutilayered_per_class_comparison'
    dtype='data_comparison'
    data_mutants_select=pd.DataFrame()
    for i in range(len(data_labels)):
        data_fn=data_fns[i]
        data_label=data_labels[i]
        data_fh='%s/data_comparison/aas/%s' % (prj_dh,data_fn)
        data_comparison=pd.read_csv(data_fh).set_index('mutids')        
        data_plot=data_comparison.copy()
        print len(denanrows(data_plot.loc[:,'class_comparison']))
        if (filter_selection=='by_side'):
            selection=fns2sides[data_fn]    	        
        else:# (filter_selection=='signi'):
            selection=data_sections_pvals.loc[data_label,'selection']
            # pval=data_sections_pvals.loc[data_label,'All']
        if selection=='positive':
            color_dots='heads'
        elif selection=='negative':
            color_dots='tails'
        print color_dots
            
        if ((filter_selection=='signi') or (filter_selection=='by_side')):
            data_comparison=data_comparison.loc[(data_comparison.loc[:,'class_comparison']==selection),:]
        else:
            data_comparison=data_comparison.loc[((data_comparison.loc[:,'class_comparison']=='positive')\
                                               | (data_comparison.loc[:,'class_comparison']=='negative')),:]            
#         data_plot=data_comparison.copy()
        if filter_sections==True:
            data_comparison=data_comparison.loc[~pd.isnull(data_comparison.loc[:,'sectionn']),:]
            sectionn='True'
        elif filter_sections=='signi':
            sectionn=data_sections_pvals.loc[data_label,'Significant section']
            data_comparison=data_comparison.loc[(data_comparison.loc[:,'sectionn']==sectionn),:]           
    # get intersect of (mutids significant section) and (class of selection) 
        else:
            sectionn='all'
        if filter_signi:
            data_comparison.loc[pd.isnull(data_comparison.loc[:,'Significant']),'Significant']=False
            data_comparison=data_comparison.loc[data_comparison.loc[:,'Significant'],:]
    # by lowest of multiplication of pvals (only empiric)
        zcol='z'
        xcol='FiA_ctrl'
        ycol='FiA_test'
        data_comparison.loc[:,zcol]=data_comparison.loc[:,'padj_test']*data_comparison.loc[:,'padj_ctrl']
    # get top 5
#         data_comparison.to_csv('test.csv')            
        mutids_heads,mutids_tails=gettopnlastdiff(data_comparison,ycol,xcol,
#                                                   zcol=zcol
                                                  col_classes='class_comparison',
                                                  classes=['positive','negative']
                                                 )
        
        data_comparison.loc[:,'data_label']=data_label
        data_comparison.loc[:,'data_fn']=data_fn
        data_mutants_select=data_mutants_select.append(data_comparison.loc[mutids_heads+mutids_tails,:])
        plot_fh='%s/plots/aas/fig_%s_section_%s_%s.pdf' % (prj_dh,plot_type,sectionn.replace(',','_'),data_fn)
        print plot_fh
        print mutids_heads
        print mutids_tails  
        if not exists(plot_fh) or force:
            note_text=None
            data_comparison2scatter_mutilayered(data_plot,data_label,
                        color_dots,note_text=note_text,
                        plot_fh=plot_fh,
                        mutids_heads=mutids_heads,
                        mutids_tails=mutids_tails,
                        col_pvals=col_pvals,
                        repel=0.08,
                        figsize=figsize,
                        )
    return data_mutants_select 