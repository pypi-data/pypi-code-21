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
import matplotlib.gridspec as gridspec
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
# matplotlib.style.use('ggplot')
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # 

from dms2dfe.lib.io_plots import saveplot
from dms2dfe.lib.io_mut_files import mutids_converter

def data2mut_matrix(data_fit,values_col,index_col,type_form): 
    """
    This creates mutation matrix from input data (frequncies `data_lbl` or `data_fit`).
    
    :param data_fit: fitness data (`data_fit`).
    :param values_col: column name with values (str). 
    :param index_col: column name with index (str).
    :param type_form: type of values ["aas" : amino acid | "cds" : codons].
    """
    from dms2dfe.lib.io_nums import str2num
    # data_fit.to_csv("data_fit1")
    if (not 'refi' in data_fit) or (any(pd.isnull(data_fit.loc[:,'refi']))) :
        data_fit.loc[:,'refi']=[str2num(mutid) for mutid in data_fit.loc[:,"mutids"].tolist()]
    data_fit=data_fit.sort_values(by="refi",axis=0)
    
    if 'aas' in type_form:   
        data_fit.loc[:,'refrefi']\
        =[("%s%03d" % (mutid[0],str2num(mutid))) for mutid in data_fit.loc[:,"mutids"].tolist()]
    elif 'cds' in type_form:
        data_fit.loc[:,'refrefi']\
        =[("%s%03d" % (mutid[:2],str2num(mutid))) for mutid in data_fit.loc[:,"mutids"].tolist()]

    data_fit_heatmap=pd.pivot_table(data_fit,values=values_col,index=index_col,columns='refrefi')
    data_fit_heatmap=data_fit_heatmap.reindex_axis(data_fit.loc[:,'refrefi'].unique(),axis='columns')

    # data_fit.to_csv("data_fit2")
    # data_fit_heatmap.to_csv("data_fit_heatmap")

    return data_fit_heatmap

def plotsspatches(ssi,ssi_ini,aai,aai_ini,patches,patches_colors,ax):
# H Alpha helix
# B Beta bridge
# E Strand
# G Helix-3
# I Helix-5
# T Turn
# S Bend
    sss=["H","B","E","G","I","T","S"]
    for ss in sss:
        if ssi==ss:
            ssi_ini=ssi
            aai_ini=aai+1
        elif ssi_ini==ss:
            width=aai+1-aai_ini
            if ss == "H":
                patch=mpatches.Arrow(aai_ini, 0, width,0, 4, edgecolor="none")
            else:
                patch=mpatches.Rectangle([aai_ini, -0.5], width, 1,edgecolor="none")                
            patches.append(patch)
            patches_colors.append(sss.index(ss))
            ssi_ini=ssi
            aai_ini=aai
            ax.text(aai_ini-width/2,0.5,ss,fontdict={'size': 16})
    return patches,patches_colors,aai_ini,ssi_ini,ax

def plotss(data_feats,ax,refi_lims,fontsize=20,ticks=False):
    if not ticks:
        ax.set_axis_off()
    #no sec struct
    for aai,rowi in data_feats.iterrows():
        if not pd.isnull(rowi.loc["Secondary structure"]):
            ini=aai+1
            break
    for aai,rowi in data_feats.iloc[::-1].iterrows():
        if not pd.isnull(rowi.loc["Secondary structure"]):
            end=aai+1
            break
    x,y = np.array([[ini, end], [0, 0]])
    line = mlines.Line2D(x, y, lw=5,color="black")
    line.set_zorder(0)
    ax.add_line(line)

    patches = []
    patches_colors=[]
    ssi_ini=""
    aai_ini=0
    for aai,rowi in data_feats.fillna("").iterrows():
        aai=aai-1
        ssi=rowi.loc["Secondary structure"]
        if ssi!=ssi_ini:
            patches,patches_colors,aai_ini,ssi_ini,ax=plotsspatches(ssi,ssi_ini,aai,aai_ini,patches,patches_colors,ax)
    collection = PatchCollection(patches, cmap=plt.cm.Accent, alpha=1)
    colors = np.linspace(0, 1, len(patches))
    collection.set_array(np.array(patches_colors))
    collection.set_zorder(20)
    ax.add_collection(collection)
    ax.set_xlim((refi_lims[0]-0.5,refi_lims[1]+0.5))
    ax.set_ylim((-1.1,1.1))
    ax.text(refi_lims[1]+1,-0.5,"%sSecondary structure" % (r'$\leftarrow$'),fontdict={'size': fontsize})
    return ax

def plotacc(data_feats,ax,refi_lims,fontsize=20,ticks=False):
    if not ticks:
        ax.set_axis_off()

    acc_cols=["Solvent accessibility","Solvent Accessible Surface Area"]
    for acc_col in acc_cols:
        if acc_col in data_feats:
            ylim=data_feats.loc[:,acc_col].max()
            ax.stackplot(data_feats.loc[:,"aasi"]-1,data_feats.loc[:,acc_col])
            ax.set_xlim((refi_lims[0]-0.5,refi_lims[1]+0.5))
            ax.set_ylim((0,ylim))
            ax.text(refi_lims[1]+1,0,"%sSolvent accessibility" % (r'$\leftarrow$'),fontdict={'size': fontsize})
            return ax    
            break
    # print [c for c in data_feats.columns if 'ccessib' in c]
    return ax

def plot_data_fit_heatmap(data_fit,type_form,col,
                            cmap="coolwarm",center=0,data_feats=None,
                            xticklabels=None,cbar_label='$F_{i}$',
                            figsize=(80, 12),
                            fontsize=20,
                            refi_lims=[],
                            note_text=True,
                            note_loc=[0.125, 0.02],
                            xticklabels_stepsize=1,
                            cbar_lims=[None,None],
                            plot_fh=None,):
    """
    This plots heatmap of fitness values.
    
    :param data_fit: input data (`data_lbl` or `data_fit`) (dataframe).
    :param type_form: type of values ["aas" : amino acid | "cds" : codons].
    :param col: eg. columns with values. col for data_fit
    :param cmap: name of colormap (str).
    :param center: center colormap to this value (int).
    :param data_feats: input features `data_feats`.
    :param xticklabels: xticklabels of heatmap ["None" : reference index | "seq" : reference sequence].
    """
    from dms2dfe.lib.io_nums import str2num
    from dms2dfe.lib.global_vars import aas_21,cds_64
    import seaborn as sns

    # if not 'refi' in data_fit:
    data_fit.loc[:,'refi']=[str2num(mutid) for mutid in data_fit.loc[:,'mutids']]    
    if len(refi_lims)==2:
        data_fit=data_fit.loc[((data_fit.loc[:,'refi']>=refi_lims[0]) &\
                               (data_fit.loc[:,'refi']<=refi_lims[1])),:]
    refi_min=data_fit.loc[:,'refi'].min()
    refi_max=data_fit.loc[:,'refi'].max()
    data_fit_heatmap  =data2mut_matrix(data_fit,col,'mut',type_form)
    refis=[str2num(i) for i in data_fit_heatmap.columns.tolist()]
    refis=np.sort(refis)
    refrefis=pd.DataFrame(data_fit_heatmap.columns.tolist(),index=refis,columns=["refrefi"])

    if len(refi_lims)==2:
        data_fit_heatmap2=data_fit_heatmap.copy()        
        xoff=np.min([str2num(mutid) for mutid in data_fit_heatmap2.columns.tolist()])       
    else:
        data_fit_heatmap2=pd.DataFrame(index=data_fit_heatmap.index)
        for i in range(1,refis[-1]+1):
            if i not in refis:
                data_fit_heatmap2.loc[:,i]=np.nan
            else :
                data_fit_heatmap2.loc[:,refrefis.loc[i,"refrefi"]]=data_fit_heatmap.loc[:,refrefis.loc[i,"refrefi"]]
        xoff=1
    data_syn_locs=data_fit.loc[(data_fit.loc[:,"ref"]==data_fit.loc[:,"mut"]),["mutids","ref",'refi']]
    data_nan_locs=data_fit.loc[pd.isnull(data_fit.loc[:,col]),["mutids","ref","mut",'refi']]

    if "aas" in type_form:
        data_syn_locs["muti"]=[20-aas_21.index(i) for i in data_syn_locs["ref"]]
        data_nan_locs["muti"]=[20-aas_21.index(i) for i in data_nan_locs["mut"]]

    if "cds" in type_form:
        cds_64.sort()
        data_syn_locs["muti"]=[63-cds_64.index(i) for i in data_syn_locs["ref"]]
        data_nan_locs["muti"]=[63-cds_64.index(i) for i in data_nan_locs["mut"]]

    plt.figure(figsize=figsize,dpi=400)      
    gs = gridspec.GridSpec(3, 1,height_ratios=[1,1,32])

    ax_all=plt.subplot(gs[:])
    sns.set(font_scale=2)
    ax = plt.subplot(gs[2])
    # print data_fit_heatmap2.shape
    sns.heatmap(data_fit_heatmap2,cmap=cmap,ax=ax,
        vmin=cbar_lims[0],vmax=cbar_lims[1]
        )

    ax.set_xlabel('Residue positions',fontdict={'size': fontsize})
    ax.set_ylabel('Mutation to',fontdict={'size': fontsize})

    if xticklabels=="seq":
        ax.set_xticklabels(data_fit_heatmap2.columns.tolist(),rotation=90)
    else:
        ax.set_xticks(np.arange(0,refi_max-refi_min,xticklabels_stepsize)+0.5)
        # print refi_min,refi_max,xticklabels_stepsize
        ax.set_xticklabels(range(refi_min,refi_max,xticklabels_stepsize),rotation=90)
    yticklabels=data_fit_heatmap2.index.values.tolist()
    ax.set_yticklabels(yticklabels[::-1],rotation=0,)

    ax.get_xaxis().set_tick_params(which='both', direction='out')
    ax.tick_params(axis='both', which='major', labelsize=fontsize)
    
    data_syn_locs=data_syn_locs.reset_index(drop=True)
    for i in data_syn_locs.reset_index().index.values:
        ax.text(data_syn_locs.loc[i,"refi"]-xoff+0.5,
            data_syn_locs.loc[i,"muti"]+0.66,
            r"$\plus$",
                fontsize=fontsize*0.5,fontweight='bold',
                ha='center',
                va='center',                
                )#,color='g')

    data_nan_locs=data_nan_locs.reset_index(drop=True)
    for i in data_nan_locs.index.values:
        ax.text(data_nan_locs.loc[i,"refi"]-xoff+0.5,
            data_nan_locs.loc[i,"muti"]+0.33,
            r"$\otimes$",
                fontsize=fontsize*0.5,fontweight='bold',
                ha='center',
                va='center',                
                )

    if not data_feats is None: 
        if not 'aasi' in data_feats:
            if 'refi' in data_feats:
                data_feats.loc[:,'aasi']=data_feats.loc[:,'refi']
            elif 'refrefi' in data_feats:
                data_feats.loc[:,'aasi']=[str2num(s) for s in data_feats.loc[:,'refrefi']]
        data_feats=data_feats.sort_values('aasi',ascending=True)
        ax_ss = plt.subplot(gs[0])
        ax_acc = plt.subplot(gs[1])

        ax_pos=ax.get_position()
        ax_ss_pos=ax_ss.get_position()
        ax_ss.set_position([ax_ss_pos.x0,ax_ss_pos.y0-0.05,ax_pos.width,ax_ss_pos.height*2])
        # ax_ss=plt.axes([ax_ss_pos.x0,ax_ss_pos.y0,ax_pos.width,ax_ss_pos.height])
        # ax_ss.set_axis_off()
        ax_acc_pos=ax_acc.get_position()
        ax_acc.set_position([ax_acc_pos.x0,ax_acc_pos.y0-0.03,ax_pos.width,ax_acc_pos.height*2])
        # ax_acc.set_axis_off()

        ax_ss=plotss(data_feats,ax_ss,refi_lims=[refi_min,refi_max],
            fontsize=fontsize,
            # ticks=True
            )
        ax_acc=plotacc(data_feats,ax_acc,refi_lims=[refi_min,refi_max],
            fontsize=fontsize,
            # ticks=True
            )
    if cbar_label!=None:
        loc=[(refi_max-refi_min)*1.1,-1]
        ax.text(loc[0],loc[1],cbar_label,va='top',ha='center',
               fontsize=fontsize)        
    if note_text==True:
        note_text_syns="%s: Synonymous mutations" % (r"$\plus$")
        note_text_nans='%s: Mutations for which data is not available' % (r"$\otimes$")
        if len(data_syn_locs)>0:
            note_text=note_text_syns
        if len(data_nan_locs)>0:
            note_text='%s\n%s' % (note_text,note_text_nans)
        if note_text==True:
            note_text=''
    loc=[0,-2.5]        
    ax.text(loc[0],loc[1],note_text,va='top',ha='left',
           fontsize=fontsize)

    saveplot(plot_fh,form='both',transparent=False,
             tight_layout=False)
    sns.set(font_scale=1)
    return ax_all,data_fit_heatmap2

def plot_clustermap(data_fit_heatmap,
                    cmap="coolwarm",center=0,
                    col_cluster=False,row_cluster=True,
                    col_cluster_label='',row_cluster_label='',
                    col_colors=None,row_colors=None,
                    xlabel='Wild type',ylabel='Mutation',
                    vmin=None, vmax=None,
                    cax_pos=[],#[.20, .2, .01, .45] #rt=[0.775, .2, .02, .45]
                    cax_label='',
                    figsize=[5,5],
                    plot_fh=None):
    """
    This clusters heatmaps.

    :param data_fit: fitness data
    :param type_form: type of mutants ["aas" : amino acid | "cds" : codon level]
    :param col: eg. columns with values. col for data_fit
    """
    import seaborn as sns
#     data_fit_heatmap  =data2mut_matrix(data_fit,col,'mut',type_form)
    plt.figure()

    # ax1=plt.subplot(121)
    # ax2=plt.subplot(122)
    # print vmin  
    ax=sns.clustermap(data_fit_heatmap.fillna(0),
                    method='average', metric='euclidean',
                      col_cluster=col_cluster,row_cluster=row_cluster,
                      col_colors=col_colors,row_colors=row_colors,
                      vmin=vmin, vmax=vmax,
#                       row_colors_ratio=0.01,
#                       cbar_kws={'vertical'},
                      cmap=cmap,
                      figsize=figsize)
#     ax.fig.colorbar(cax=ax1)
    ax.ax_heatmap.set_xlabel(xlabel)
    ax.ax_heatmap.set_ylabel(ylabel)
#     print 
    if col_cluster_label!='':
        ax.ax_heatmap.text(ax.ax_heatmap.get_xlim()[1],ax.ax_heatmap.get_ylim()[1],
                              '%s' % (r'$\leftarrow$'),
                              va='bottom')
        ax.ax_heatmap.text(ax.ax_heatmap.get_xlim()[1]+2,ax.ax_heatmap.get_ylim()[1],
                          col_cluster_label.replace(' ','\n'),
                          va='bottom')
    if row_cluster_label!='':    
        # ax.ax_heatmap.text(ax.ax_heatmap.get_xlim()[0]-1,ax.ax_heatmap.get_ylim()[1],
        #                       '%s' % (r'$\downarrow$'),
        #                       va='bottom')
        # ax.ax_heatmap.text(ax.ax_heatmap.get_xlim()[0],ax.ax_heatmap.get_ylim()[1]+1,
        #                   row_cluster_label.replace(' ','\n'),
        #                   va='bottom',
        #                   ha='right')
        ax.ax_heatmap.text(ax.ax_heatmap.get_xlim()[0]-1,ax.ax_heatmap.get_ylim()[0]-1,
                              '%s' % (r'$\uparrow$'),
                              va='bottom',
                              ha='center',)
        ax.ax_heatmap.text(ax.ax_heatmap.get_xlim()[0],ax.ax_heatmap.get_ylim()[0]-3,
                          row_cluster_label.replace(' ','\n'),
                          va='bottom',
                          ha='right')


#         if not col_cluster:
#             ax.ax_heatmap.set_xticks(range(1,len(data_fit_heatmap.columns),20),rotation=90)
#             ax.ax_heatmap.set_xticklabels(range(1,len(data_fit_heatmap.columns),20),
#                                           rotation=90)
    ax.ax_heatmap.set_xticklabels(ax.ax_heatmap.get_xticklabels(),rotation=0)
    ax.ax_heatmap.set_yticklabels(ax.ax_heatmap.get_yticklabels(),rotation=0)
        # ax.cax.set_position([.20, .2, .01, .45])
    # plot_margin = 0.25

    # x0, x1, y0, y1 = plt.axis()
    # plt.axis((x0 - plot_margin,
    #           x1 + plot_margin,
    #           y0 - plot_margin,
    #           y1 + plot_margin))
    # plt.subplots_adjust(left=0, bottom=0, right=0.5, top=0.5, wspace=0, hspace=0)
    if len(cax_pos)==4:
        ax.fig.subplots_adjust(right=0.65)
        ax.cax.set_position(cax_pos)
        ax.cax.set_xlabel(cax_label)
    if plot_fh!=None:
        # saveplot(plot_fh)
        plt.savefig(plot_fh,format='pdf')
        # plt.savefig(plot_fh+'.svg',format='svg')
        plt.clf();plt.close()
    return ax

from dms2dfe.lib.io_dfs import denanrows
from dms2dfe.lib.plot_mut_data import data2sub_matrix
from dms2dfe.lib.io_plots import get_rgb_colors

def make_plot_cluster_sub_matrix(data_combo,xcol,boundaries,
                                 feats,
                                 feats_labels,
                                 row_cluster=True,
                                 col_cluster=True,
                                 test=False,
                                 plot_fh=None):
    # data_combo_fh='%s/data_feats/data_fit_boxplot_per_feat_%s.csv' % (prj_dh,data_fit_fn)
    # data_combo=pd.read_csv(data_combo_fh).set_index('mutids')
    if not 'mutids' in data_combo:
        data_combo=data_combo.reset_index()
#     xcol='%s: FiA' % data_fit_fn
    cols=[xcol,'mut','ref','refrefi']+feats
    for col in cols:
        if not col in data_combo:
            # print col
            data_combo.loc[:,col]=mutids_converter(data_combo.loc[:,'mutids'],
                                                   col, 'aas')
            # break
    data_combo=denanrows(data_combo.loc[:,cols])
    # return data_combo.shape
    
    # data_combo.head()
    featn=feats[1]
    data_feat_ref=pd.DataFrame()
    data_feat_ref.loc[:,featn]=data2sub_matrix(data_combo, featn,
                                               'mut','aas',
                                               aggfunc='mean').sum()
    data_feat_ref.loc[(data_feat_ref.loc[:,featn]==0),featn]=data_feat_ref.loc[:,featn].min()
#     print data_feat_ref.loc[:,featn]
    # print data_feat_ref.loc[:,featn]
    col_colors=get_rgb_colors(data_feat_ref.loc[:,featn])
    featn=feats[0]
    data_feat_ref.loc[:,featn]=data2sub_matrix(data_combo, featn,
                                               'mut','aas',
                                               aggfunc='mean').T.sum()
    data_feat_ref.loc[(data_feat_ref.loc[:,featn]==0),featn]=data_feat_ref.loc[:,featn].min()
    row_colors=get_rgb_colors(data_feat_ref.loc[:,featn])
    
    # for quant in [0,0.25,0.5,0.75]:
    for quant in boundaries:
#         print quant
        if plot_fh is None:
            plot_out_fh='%s_%s_to_%s.pdf' % (plot_fh,quant[0],quant[1])
        else:
            plot_out_fh=plot_fh
        # print plot_out_fh
        cutoff_dw=data_combo.loc[:,featn].quantile(q=quant[0])
        cutoff_up=data_combo.loc[:,featn].quantile(q=quant[1])
        data=data_combo.loc[((data_combo.loc[:,featn]>cutoff_dw) & (data_combo.loc[:,featn]<=cutoff_up)),cols]
        sub_matrix=data2sub_matrix(data, xcol,'mut','aas', aggfunc='mean')
        ax=plot_clustermap(sub_matrix,
                            row_cluster=row_cluster,
                            col_cluster=col_cluster,
                            row_cluster_label=feats_labels[0],
                            col_cluster_label=feats_labels[1],                           
                            row_colors=row_colors,
                            col_colors=col_colors,
                            cax_pos=[0.75, .2, .02, .45],
                            cax_label='$F_{i}$',#'$F_{i}$\n(average)',
                            figsize=[6,4],
                            plot_fh=plot_out_fh
                                )
        if test:
            return ax
            break

# sns.set(font="monaco")
def clustermap(df,highlight_xywhs=[],
               highlight_col=None,
               vlim=[-0.8,0.8],
               if_xticks_rotate=False,
              figsize=(4, 4),
              plot_fh=None):
    import seaborn as sns
    import scipy.cluster.hierarchy as sch
    from scipy.cluster.hierarchy import fcluster
    Y = sch.linkage(df, method='centroid')
    clusters=fcluster(Y,t=0.75)
    # feats2clusters=pd.DataFrame({'feature':df.columns,
    #                             'cluster':clusters})
    pal=sns.color_palette("husl", len(np.unique(clusters)))
    lut = dict(zip(map(str, np.unique(clusters)), pal))
    # Convert the palette to vectors that will be drawn on the side of the matrix 
    colors=[lut[str(i)] for i in clusters]
    colors = pd.Series(colors, index=df.columns)
    colors.name='Cluster'
    g=sns.clustermap(df.corr(), row_colors=colors,
                   col_colors=colors, 
                     figsize=figsize,
                    vmin=vlim[0],vmax=vlim[1],
                   cmap='RdBu_r',
                    cbar_kws={'label': '$\\rho$'})
    plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0)
    ax = g.ax_heatmap
    if not highlight_col is None:
        xticklabels=[s.get_text() for s in g.ax_heatmap.get_xticklabels()]
        yticklabels=[s.get_text() for s in g.ax_heatmap.get_yticklabels()]
        highlight_xywhs.append([0,yticklabels.index(highlight_col),df.shape[1],1])
        highlight_xywhs.append([xticklabels.index(highlight_col),0,1,df.shape[0]]) 
    #print highlight_xywhs 
    for xywh in highlight_xywhs:
        from matplotlib.patches import Rectangle        
        ax.add_patch(Rectangle((xywh[0], xywh[1]), xywh[2], xywh[3],
                               fill=False, edgecolor='lime', lw=3))
    ax.figure.subplots_adjust(left=0,right=0.55,
                              bottom=0.35,top=0.9,
                              wspace = 0.5,hspace = 0.5,
                             ) 
    if not plot_fh is None:
        saveplot(plot_fh,tight_layout=False)
    return g,ax
