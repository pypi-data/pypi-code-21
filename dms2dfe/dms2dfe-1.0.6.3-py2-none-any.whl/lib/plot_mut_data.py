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
from dms2dfe.lib.global_vars import mut_types_form


def plot_data_lbl_repli(prj_dh,lim_min=0):
    """
    This plots scatters of frequecies of replicates.
    
    :param prj_dh: path to project directory.   
    """    
    
    repli=pd.read_csv('%s/cfg/repli' % prj_dh).set_index("varname",drop=True)
    if "Unnamed: 0" in repli.columns:
        repli=repli.drop("Unnamed: 0", axis=1)

    for i,replii in repli.iterrows():
        replii=[str(lbl) for lbl in replii if not 'nan' in str(lbl)] # if not 'nan' in lbl
        if len(replii)!=0:
            for type_form in mut_types_form:
                if not exists("%s/plots/%s" % (prj_dh,type_form)):
                    makedirs("%s/plots/%s" % (prj_dh,type_form))
                data_lbl_key="data_lbl/%s/%s" % (type_form,replii[0])
                plot_fh="%s/plots/%s/fig_repli_%s.pdf" % (prj_dh,type_form,data_lbl_key.replace('/','_'))
                if not exists(plot_fh): 
                    data_repli=pd.DataFrame()
                    data_repli_usable=[]
                    for lbl in replii:
                        data_lbl_fh= "%s/data_lbl/%s/%s" % (prj_dh,type_form,lbl)
                        try:
                            data_lbl=pd.read_csv(data_lbl_fh)
                            data_repli[lbl]=data_lbl['NiAcutlog']#.fillna(0)
                            if len(data_repli.loc[:,lbl].unique())>10:
                                data_repli_usable.append(True)
                            else:
                                data_repli_usable.append(False)
                        except:
                            logging.warning("do not exist: %s" % lbl)
                    data_repli=data_repli.loc[:,data_repli_usable]
                    plot_corr_mat(data_repli,plot_fh,xlim=(lim_min,None),ylim=(lim_min,None))
                else:
                    logging.info("already processed: %s" % basename(plot_fh))

def annotate_pearsonr(x, y, **kws):
    from scipy import stats
    r, _ = stats.pearsonr(x, y)
    ax = plt.gca()
    ax.annotate("r = {:.2f}".format(r),
            xy=(.1, .9), xycoords=ax.transAxes)
                    
def plot_corr_mat(data_repli,plot_fh=None,xlim=(0,None),ylim=(0,None)):
    import seaborn as sns
    from dms2dfe.lib.io_ml import denanrows
    # data_repli=data_repli.loc[:,data_repli_usable]
    data_repli=denanrows(data_repli)
    if len(data_repli.columns)!=0:
        ax=sns.pairplot(data_repli,diag_kind="kde",kind="reg")
        ax.set(xlim=xlim,ylim=ylim)
        ax.map_lower(annotate_pearsonr)
        ax.map_upper(annotate_pearsonr)
        plt.tight_layout()
        if plot_fh!=None:
            plt.savefig(plot_fh,format='pdf')  
            plt.clf();plt.close()
        return ax

def plot_data_fit_scatter(data_fit,norm_type,Ni_cutoff,plot_fh=None):
    """
    This plots scatter plot of frequecies of selected and unselected samples.
    
    :param data_fit: fitness data (`data_fit`). 
    :param norm_type: Type of normalization across samples [wild: wrt wild type | syn : wrt synonymous mutations | none : fold change serves as fitness]
    :param Ni_cutoff: threshold of depth per codon to be processed further. 
    """
    if np.isinf(np.log2(Ni_cutoff)):
        ax_lim_min=0 
    else:
        ax_lim_min=np.log2(Ni_cutoff)
    ax_lim_max=np.ceil(np.max([data_fit.loc[:,'NiAunsel'].max(),data_fit.loc[:,'NiAsel'].min()*-1]))+3
    
    # fig = 
    plt.figure(figsize=(3, 3),dpi=500)
    ax=plt.subplot(111)
    # plt.gcf().subplots_adjust(bottom=0.15)
    if norm_type=="syn":
        data_fit.plot(kind='scatter', x='NiAunsel', y='NiAsel', \
                           color='Black', label='Non-synonymous', ax=ax)
        data_fit.plot(kind='scatter', x='NiSunsel', y='NiSsel', \
                      color='darkorange', label='Synonymous', ax=ax)
    else:
        data_fit.plot(kind='scatter', x='NiAunsel', y='NiAsel', \
                           color='Black', label=None, ax=ax)    
    ax.set_xlabel(r'$N_{i,unsel}$')
    ax.set_ylabel(r'$N_{i,sel}$')
    ax.set_xlim([ax_lim_min,ax_lim_max])
    ax.set_ylim([ax_lim_min,ax_lim_max])
    ax.legend(loc= "upper right",frameon=True)
    plt.tight_layout()
    if plot_fh!=None:
        plt.savefig(plot_fh,format='pdf')
        plt.clf();plt.close()
    return ax

def plot_data_fit_dfe(data_fit,norm_type=None,col_fit="FiA",
                      annot_X=True,annot_syn=False,
                      xlabel=r'$F_{i}$',
                      axvspan_min=0,axvspan_max=0,
                      plot_fh=None):
    """
    This plots histogram of Distribution of Fitness Effects (DFE).
    
    :param data_fit: fitness data (`data_fit`).
    :param norm_type: Type of normalization across samples [wild: wrt wild type | syn : wrt synonymous mutations | none : fold change serves as fitness]
    """
    plt.style.use('seaborn-white')
    # fig = 
    plt.figure(figsize=(6, 2.25),dpi=300)
    ax=plt.subplot(111)
#     if norm_type=="syn":
#         if not 'FiS' in data_fit.columns.tolist():
#                 data_fit.loc[:,'FiS']=data_fit.loc[(data_fit_infered.loc[:,'ref']==data_fit.loc[:,'mut']),col_fit]
        
#         data_fit[[col_fit,'FiS']].plot(kind='hist',bins=40,
#                                color='limegreen',ax=ax,zorder=3,alpha=0.75)
#         l2=ax.legend(['Non-synonymous','Synonymous'],loc="upper right")
#     else:
    data_fit[col_fit].plot(kind='hist',bins=40,
                           color='limegreen',
                           edgecolor='k',
                           ax=ax,zorder=3,alpha=0.75)    
    xlim=np.ceil(np.max([data_fit.loc[:,col_fit].max(),data_fit.loc[:,col_fit].min()*-1]))
    ax.axvspan(-xlim, axvspan_min, color='blue', alpha=0.05)
#     ax.axvspan(axvspan_min, axvspan_max, color='grey', alpha=0.05)
    ax.axvspan(axvspan_max, xlim, color='red', alpha=0.05)
    # l1=ax.legend(['Deleterious','Neutral','Beneficial'], loc='upper left')
    
    ymin,ymax=ax.get_ylim()
    
    if annot_X:
        data_fit_X=data_fit.loc[data_fit.loc[:,"mut"]=="X",col_fit]
        for i in list(data_fit_X):
            ax.axvline(x=i, ymin=ymin, ymax=ymax,color="k",zorder=0)

    if annot_syn:
        data_fit_X=data_fit.loc[data_fit.loc[:,"mut"]=="X",col_fit]
        ax.axvline(x=0, ymin=ymin, ymax=ymax,color="gray",zorder=1)

    ax.legend(['Mutation to\nstop codon'],loc="upper right",frameon=True)

    ax.set_xlabel(xlabel)
    ax.set_ylabel('Count')
    ax.set_xlim(-xlim,xlim)
    plt.tight_layout()
    if plot_fh!=None:
        plt.savefig(plot_fh,format='pdf')
        plt.clf();plt.close()
    return ax

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

def plotss(data_feats,ax):
#     plt.figure(figsize=(40, 1),dpi=500)
#     ax=plt.subplot(111)
    ax.set_axis_off()
    xlim=len(data_feats)

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
    # ax.set_xticklabels(range(xlim))
    ax.set_xlim((0-0.5,xlim+0.5))
    ax.set_ylim((-1.1,1.1))
    ax.text(xlim+1,-0.5,"Secondary structure",fontdict={'size': 20})
#     plt.show()
    return ax

def plotacc(data_feats,ax):
    ax.set_axis_off()
    xlim=len(data_feats)

    acc_cols=["Solvent accessibility","Solvent Accessible Surface Area"]
    for acc_col in acc_cols:
        if acc_col in data_feats:
            ylim=data_feats.loc[:,acc_col].max()
            ax.stackplot(data_feats.loc[:,"aasi"]-1,data_feats.loc[:,acc_col])
            ax.set_xlim((0-0.5,xlim+0.5))
            ax.set_ylim((0,ylim))
            ax.text(xlim+1,0,acc_col,fontdict={'size': 20})
            return ax    
            break
    print [c for c in data_feats.columns if 'ccessib' in c]
    return ax

# def plot_data_fit_heatmap(data_fit,type_form,col,\
#                           cmap="coolwarm",center=0,data_feats=None,xticklabels=None,plot_fh=None,cbar_label=None):
#     """
#     This plots heatmap of fitness values.
    
#     :param data_fit: input data (`data_lbl` or `data_fit`) (dataframe).
#     :param type_form: type of values ["aas" : amino acid | "cds" : codons].
#     :param col: eg. columns with values. col for data_fit
#     :param cmap: name of colormap (str).
#     :param center: center colormap to this value (int).
#     :param data_feats: input features `data_feats`.
#     :param xticklabels: xticklabels of heatmap ["None" : reference index | "seq" : reference sequence].
#     """
#     from dms2dfe.lib.io_nums import str2num
#     from dms2dfe.lib.global_vars import aas_21,cds_64
#     import seaborn as sns
    
#     data_fit_heatmap  =data2mut_matrix(data_fit,col,'mut',type_form)
#     refis=[str2num(i) for i in data_fit_heatmap.columns.tolist()]
#     refis=np.sort(refis)
#     refrefis=pd.DataFrame(data_fit_heatmap.columns.tolist(),index=refis,columns=["refrefi"])

#     data_fit_heatmap2=pd.DataFrame(index=data_fit_heatmap.index)
#     for i in range(1,refis[-1]+1):
#         if i not in refis:
#             data_fit_heatmap2.loc[:,i]=np.nan
#         else :
#             data_fit_heatmap2.loc[:,refrefis.loc[i,"refrefi"]]=data_fit_heatmap.loc[:,refrefis.loc[i,"refrefi"]]

#     data_syn_locs=data_fit.loc[(data_fit.loc[:,"ref"]==data_fit.loc[:,"mut"]),["mutids","ref"]]
#     data_syn_locs["refi"]=[str2num(i)-1+0.05 for i in data_syn_locs["mutids"]]

#     data_nan_locs=data_fit.loc[pd.isnull(data_fit.loc[:,col]),["mutids","ref","mut"]]
#     data_nan_locs["refi"]=[str2num(i)-1+0.05 for i in data_nan_locs["mutids"]]


#     if "aas" in type_form:
#         data_syn_locs["muti"]=[20-aas_21.index(i)+0.15 for i in data_syn_locs["ref"]]
#         data_nan_locs["muti"]=[20-aas_21.index(i)+0.15 for i in data_nan_locs["mut"]]

#     if "cds" in type_form:
#         cds_64.sort()
#         data_syn_locs["muti"]=[63-cds_64.index(i)+0.15 for i in data_syn_locs["ref"]]
#         data_nan_locs["muti"]=[63-cds_64.index(i)+0.15 for i in data_nan_locs["mut"]]

#     # fig=
#     plt.figure(figsize=(80, 12),dpi=300)      
#     # fig=plt.figure(figsize=(40, 6),dpi=500)      
#     gs = gridspec.GridSpec(3, 1,height_ratios=[1,1,32])


#     ax_all=plt.subplot(gs[:])
#     ax_all.set_axis_off()

#     ax = plt.subplot(gs[2])
#     result=sns.heatmap(data_fit_heatmap2,cmap=cmap,ax=ax)
#     ax.set_xlabel('Wild type',fontdict={'size': 20})
#     ax.set_ylabel('Mutation to',fontdict={'size': 20})
#     cbar=ax.figure.colorbar(ax.collections[0])
#     if cbar_label==None:
#         cbar.set_label(("$%s$" % col),fontdict={'size': 20})
#     else:
#         cbar.set_label(("%s" % cbar_label),fontdict={'size': 20})
#     # print len(data_fit_heatmap2.columns.tolist())
#     # print len(range(1,len(data_fit_heatmap2.columns)+1,1))
#     if xticklabels=="seq":
#         ax.set_xticklabels(data_fit_heatmap2.columns.tolist(),rotation=90)
#     else:
#         ax.set_xticks(np.arange(1,len(data_fit_heatmap2.columns)+1,1)-0.35)
#         ax.set_xticklabels(range(1,len(data_fit_heatmap2.columns)+1,1),rotation=90)
#     yticklabels=data_fit_heatmap2.index.values.tolist()
#     ax.set_yticklabels(yticklabels[::-1],rotation=0)

#     data_syn_locs=data_syn_locs.reset_index(drop=True)
#     for i in data_syn_locs.reset_index().index.values:
#         ax.text(data_syn_locs.loc[i,"refi"],data_syn_locs.loc[i,"muti"],r"$\plus$")#,color='g')

#     data_nan_locs=data_nan_locs.reset_index(drop=True)
#     for i in data_nan_locs.index.values:
#         ax.text(data_nan_locs.loc[i,"refi"],data_nan_locs.loc[i,"muti"],r"$\otimes$")#,color='gray')

#     if not data_feats is None: 
#         if not 'aasi' in data_feats:
#             if 'refi' in data_feats:
#                 data_feats.loc[:,'aasi']=data_feats.loc[:,'refi']
#             elif 'refrefi' in data_feats:
#                 data_feats.loc[:,'aasi']=[str2num(s) for s in data_feats.loc[:,'refrefi']]        
#         data_feats=data_feats.sort('aasi',ascending=True)
#         ax_ss = plt.subplot(gs[0])
#         ax_acc = plt.subplot(gs[1])

#         ax_pos=ax.get_position()
#         ax_ss_pos=ax_ss.get_position()
#         ax_ss.set_position([ax_ss_pos.x0,ax_ss_pos.y0-0.05,ax_pos.width,ax_ss_pos.height*2])
#         # ax_ss=plt.axes([ax_ss_pos.x0,ax_ss_pos.y0,ax_pos.width,ax_ss_pos.height])
#         ax_ss.set_axis_off()
#         ax_acc_pos=ax_acc.get_position()
#         ax_acc.set_position([ax_acc_pos.x0,ax_acc_pos.y0-0.03,ax_pos.width,ax_acc_pos.height*2])
#         ax_acc.set_axis_off()

#         ax_ss=plotss(data_feats,ax_ss)
#         ax_acc=plotacc(data_feats,ax_acc)
#     # extent = ax_all.get_window_extent().transformed(ax_all.figure.dpi_scale_trans.inverted())
#     # extent.set_points(np.array([[5,0],[36,11]]))    
#     # extent.set_points(np.array([[5,0],[36,11]]))    
#     plt.figtext(0.125, .02, "%s: Synonymous mutations \n%s: Mutations for which data is not available" % (r"$\plus$",r"$\otimes$"),\
#                 fontdict={'size': 20})
#     if plot_fh!=None:
#         plt.savefig(plot_fh,format='pdf') 
#         plt.clf();plt.close()
#     return ax_all


def plot_data_comparison_bar(data_comparison,plot_fh=None,index=[]):
    """
    This plots the proportion of mutants according to type of selection in effect.
    
    :param data_comparison: input `data_comparison` (dataframe).
    """
    # fig = 
    plt.figure(figsize=(3, 3))
    ax=plt.subplot(111)
    
    if len(index)==0:
        index=["positive","negative","robust"]
    
    plot_data=pd.DataFrame(index=index,columns=["count"])
    group_data=pd.DataFrame(data_comparison.groupby("class_comparison").count().loc[:,"mutids"])
    for i in index:
        if i in group_data.index.values:
            plot_data.loc[i,"count"]=group_data.loc[i,"mutids"]

    plot_data.plot(kind="bar",ax=ax)
    # ax.set_xlabel('Classes of comparison')
    ax.set_ylabel('Count')
    ax.legend().set_visible(False)
    plt.tight_layout()
    if plot_fh!=None:
        plt.savefig(plot_fh,format='pdf')                        
        plt.clf();plt.close()
    return ax

def plot_data_comparison_violin(data_comparison,plot_fh=None,stars=True):
    import seaborn as sns
    data_violin=pd.DataFrame(columns=["type of sample","$F_{i}$"],index=range(len(data_comparison)*2))
    data_violin.loc[:,"$F_{i}$"]=data_comparison.loc[:,"Fi_ctrl"]
    data_violin.loc[:,"type of sample"]="control"
    data_violin.loc[len(data_comparison):len(data_comparison)+len(data_comparison),"type of sample"]="test"
    data_violin.loc[len(data_comparison):len(data_comparison)+len(data_comparison),"$F_{i}$"]\
    =list(data_comparison.loc[:,"Fi_test"])
    plt.figure(figsize=(3,3),dpi=300)
    ax=plt.subplot(111)
    sns.violinplot(x="type of sample", y="$F_{i}$", data=data_violin,scale="width",ax=ax)
    ax.set_xlabel("")

    if stars:
        from scipy.stats import mannwhitneyu
        def pval2stars(pval):
            if pval < 0.0001:
                return "****"
            elif (pval < 0.001):
                return "***"
            elif (pval < 0.01):
                return "**"
            elif (pval < 0.05):
                return "*"
            else:
                return "ns"

        y_max=np.max([data_comparison.loc[:,"Fi_test"].max(),data_comparison.loc[:,"Fi_ctrl"].max()])
        y_min=np.min([data_comparison.loc[:,"Fi_test"].min(),data_comparison.loc[:,"Fi_ctrl"].min()])
        z, pval = mannwhitneyu(data_comparison.loc[:,"Fi_test"],data_comparison.loc[:,"Fi_ctrl"],alternative='two-sided')
        ax.annotate("", xy=(0, y_max+1), xycoords='data', xytext=(1, y_max+1), textcoords='data',
                    arrowprops=dict(arrowstyle="-", ec='k',connectionstyle="bar,fraction=0.2",alpha=1))
        ax.text(0.5, y_max+4, pval2stars(pval),horizontalalignment='center',verticalalignment='center')
        ax.set_ylim([y_min-1,y_max+5])
    plt.tight_layout()
    if plot_fh!=None:
        plt.savefig(plot_fh,format='pdf')
        plt.clf();plt.close()
    return ax
# def plot_data_fit_clustermap(data_fit,type_form,col,cmap="coolwarm",center=0,col_cluster=False,row_cluster=True,plot_fh=None):
#     """
#     This clusters heatmaps.
    
#     :param data_fit: fitness data
#     :param type_form: type of mutants ["aas" : amino acid | "cds" : codon level]
#     :param col: eg. columns with values. col for data_fit
#     """
#     import seaborn as sns
#     data_fit_heatmap  =data2mut_matrix(data_fit,col,'mut',type_form)
#     plt.figure()
#     ax=sns.clustermap(data_fit_heatmap.fillna(0),method='average', metric='euclidean',\
#                       col_cluster=col_cluster,row_cluster=row_cluster)
#     ax.ax_heatmap.set_xlabel('Wild type')
#     ax.ax_heatmap.set_ylabel('Mutation to')
#     if not col_cluster:
#         ax.ax_heatmap.set_xticks(range(1,len(data_fit_heatmap.columns),20))
#         ax.ax_heatmap.set_xticklabels(range(1,len(data_fit_heatmap.columns),20),rotation=90)
#     if plot_fh!=None:
#         plt.savefig(plot_fh,format='pdf')
#         plt.clf();plt.close()
#     return ax

def data2sub_matrix(data_fit,values_col,index_col,type_form,aggfunc='mean'): 
    """
    This creates substitition matrix from input data (frequncies `data_lbl` or `data_fit`).
    
    :param data_fit: fitness data (`data_fit`).
    :param values_col: column name with values (str). 
    :param index_col: column name with index (str).
    :param type_form: type of values ["aas" : amino acid | "cds" : codons].
    """                  
    from dms2dfe.lib.global_vars import aas_21,cds_64
    if aggfunc=="mean":
        data_sub_matrix=pd.pivot_table(data_fit,values=values_col,index=index_col,columns='ref')
    else:
        data_sub_matrix=pd.pivot_table(data_fit,values=values_col,index=index_col,columns='ref',aggfunc=aggfunc)        
    #make it 21X21
    if type_form=="aas":
        sub_matrix=pd.DataFrame(index=aas_21,columns=aas_21)
        sub_matrix.index.name='Mutation to'
        sub_matrix.columns.name='Wild type'
        for ref in aas_21:
            for mut in aas_21:
                try:
                    sub_matrix.loc[mut,ref]=data_sub_matrix.loc[mut,ref]
                except:
#                     a=1
                    sub_matrix.loc[mut,ref]=np.nan
    return sub_matrix.astype(float)

def plot_sub_matrix(data_fit,type_form,col,cmap="coolwarm",center=0,plot_fh=None):
    """
    This plots heatmap of fitness values.
    
    :param data_fit: input data (`data_lbl` or `data_fit`) (dataframe).
    :param type_form: type of values ["aas" : amino acid | "cds" : codons].
    :param col: eg. columns with values. col for data_fit
    :param cmap: name of colormap (str).
    :param center: center colormap to this value (int).
    """
    from dms2dfe.lib.io_nums import str2num
    import seaborn as sns
    from dms2dfe.lib.global_vars import aas_21

    sub_matrix  =data2sub_matrix(data_fit,col,'mut',type_form)

    data_syn_locs=pd.DataFrame(columns=["refi","muti"])
    rowi=0
    for i in range(len(aas_21)):
        data_syn_locs.loc[rowi,"refi"]=i
        data_syn_locs.loc[rowi,"muti"]=len(aas_21)-i+0.25-1
        rowi+=1

#     data_nan_locs=sub_matrix.loc[pd.isnull(data_fit.loc[:,col]),["mutids","ref","mut"]]

    data_nan_locs=pd.isnull(sub_matrix).stack().reset_index()
    data_nan_locs.columns=["mut","ref","isnan"]
    data_nan_locs=data_nan_locs.loc[data_nan_locs.loc[:,"isnan"]==True,:]

    # get_refi muti
    data_nan_locs["muti"]=[20-aas_21.index(i)+0.15 for i in data_nan_locs["mut"]]
    data_nan_locs["refi"]=[aas_21.index(i) for i in data_nan_locs["ref"]]

    plt.figure(figsize=(5,4),dpi=300)
    ax=plt.subplot(111)
    result=sns.heatmap(sub_matrix,cmap=cmap,ax=ax,cbar=False)
#     ax.set_xlabel('Wild type')
#     ax.set_ylabel('Mutation to')
    yticklabels=sub_matrix.index.values.tolist()
    ax.set_yticklabels(yticklabels[::-1],rotation=0)
    
    data_syn_locs=data_syn_locs.reset_index(drop=True)
    for i in data_syn_locs.reset_index().index.values:
        ax.text(data_syn_locs.loc[i,"refi"],data_syn_locs.loc[i,"muti"],r"$\plus$")#,color='g')

    data_nan_locs=data_nan_locs.reset_index(drop=True)
    for i in data_nan_locs.index.values:
        ax.text(data_nan_locs.loc[i,"refi"],data_nan_locs.loc[i,"muti"],r"$\otimes$")#,color='gray')
    cbar=ax.figure.colorbar(ax.collections[0])
    cbar.set_label("$F_{i}$")
    plt.figtext(0.075, 0.00, "%s: Synonymous substitutions \t%s: Substitutions for which data is not available" % (r"$\plus$",r"$\otimes$"),
    # plt.figtext(0.075, -0.05, "\n%s: Substitutions for which data is not available" % (r"$\otimes$"),\
                    fontdict={'size': 9}
               )   
    ax.axis("equal")
    plt.tight_layout()
    if plot_fh!=None:
        plt.savefig(plot_fh,format='pdf')
        plt.clf();plt.close()
    return ax

def plot_cov(data_cov,data_lbl,plot_fh=None):
    plt.figure(figsize=[6,3],dpi=300)
    ax1=plt.subplot(111)
    ax1.plot(data_cov,lw=2,color='b')
    ax2 = ax1.twinx()
    ax2.plot(data_lbl,
             lw=2,color='r')
    ax1.set_xlabel("Position")
    ax1.set_ylabel("Coverage\n(number of reads per codon)",color='b')
    ax2.set_ylabel("Total number of\nmutations per codon",color='r')
    ax1.set_xlim([data_cov.index.values[0],data_cov.index.values[-1]])
    ax1.set_yscale('log')
    ax2.set_yscale('log')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    plt.tight_layout()
    if plot_fh!=None:
        plt.savefig(plot_fh,format='pdf')
        plt.clf();plt.close()
    return ax1,ax2
