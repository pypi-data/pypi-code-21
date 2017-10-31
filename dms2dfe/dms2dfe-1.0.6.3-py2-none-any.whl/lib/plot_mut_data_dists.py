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

from dms2dfe.lib.io_stats import get_wilcoxon,pval2stars
from dms2dfe.lib.io_dfs import fhs2data_combo

def plot_data_comparison_multiviolin(prj_dh,data_fits,col,
                                     data_fiti_ctrl=0,
                                     aasORcds="aas",
                                     ns=True,numeric=False,
                                     color_test=(0.6, 0.8, 1),#'mediumpurple'#"lime"
                                     color_ctrl="lightgray",    
                                     data_fits_labels=None,
                                     pval=True,
                                     stars=True,
                                     violin_width=0.9,
                                     color_xticks=None,
                                     force=False,
                                     ylims=None,
                                     col_hue='Conditions',
                                    label_test='Test',
                                    label_ctrl='Control',
                                    ylabel=None,
                                     figsize=[4,3],
                                     plot_fh=None):
    data_fit_fhs=["%s/data_fit/%s/%s" % (prj_dh,aasORcds,s) for s in data_fits]
    if plot_fh!=None:
        data_comparison_ctrl_fh=plot_fh+"data_comparison_ctrl.csv"
        data_comparison_test_fh=plot_fh+"data_comparison_test.csv"
    else:
        data_comparison_ctrl_fh="data_comparison_ctrl.csv"
        data_comparison_test_fh="data_comparison_test.csv"
    if (not exists(data_comparison_ctrl_fh)) or\
        (not exists(data_comparison_test_fh)) or force:

        data_fit_test_fhs=[fh for i,fh in enumerate(data_fit_fhs) if i!=0]
        data_fit_ctrl_fhs=[fh for i,fh in enumerate(data_fit_fhs) if i==0]
        data_comparison_test=fhs2data_combo(data_fit_test_fhs,[col],index='mutids')
        data_comparison_ctrl=fhs2data_combo(data_fit_ctrl_fhs,[col],index='mutids')

        data_comparison_test.columns=data_fits[1:]    
        data_comparison_ctrl.columns=data_fits[1:]    
        #data_comparison_test.to_csv(data_comparison_test_fh)
        #data_comparison_ctrl.to_csv(data_comparison_ctrl_fh)
    else:    
        data_comparison_test=pd.read_csv(data_comparison_test_fh).set_index('mutids')
        data_comparison_ctrl=pd.read_csv(data_comparison_ctrl_fh).set_index('mutids')

    data_all=pd.concat([data_comparison_ctrl.loc[:,data_comparison_ctrl.columns.tolist()[0]],
                        data_comparison_test],axis=1)
    data_all.columns=data_fits

    data_comparison_test=data_comparison_test.unstack().reset_index()
    data_comparison_ctrl=data_comparison_ctrl.unstack().reset_index()

    data_comparison_test.columns=["condi","mutids",col]
    data_comparison_ctrl.columns=["condi","mutids",col]

    data_comparison_test.loc[:,col_hue]=label_test
    data_comparison_ctrl.loc[:,col_hue]=label_ctrl
    data_comparison=data_comparison_test.append(data_comparison_ctrl)
        
    y_max=data_comparison.loc[:,col].max()
    y_min=data_comparison.loc[:,col].min()

    data_fit_ctrl=data_fits[data_fiti_ctrl]
    data_fit_tests=[s for s in data_fits if data_fits.index(s)!=data_fiti_ctrl]

    # fig=
    plt.figure(figsize=figsize,dpi=300)
    ax=plt.subplot(111)
    import seaborn as sns
    from scipy.stats import mannwhitneyu,wilcoxon
#     plt.style.use('seaborn-whitegrid')
#     plt.style.use('seaborn-white')
    sns.violinplot(x="condi", y=col, 
                   hue=col_hue,
                   split=True,
                   data=data_comparison,
#                    color='m',
                   palette={label_test: color_test,
                            label_ctrl: color_ctrl},
                   inner="quartile",
                   width=violin_width,
                   cut=0, 
                   # bw=0.1,
                   scale="width",ax=ax)
    plt.legend(title=col_hue,loc='upper center',
               bbox_to_anchor=(0.5, 1.1),#, 1., .102),
               ncol=2, borderaxespad=0.1,frameon=True,
              )
    ax.set_xlabel("")
    if not ylabel is None:
        ax.set_ylabel(ylabel)
#     ax.grid(b=True)
    ax.yaxis.grid(True)
    if data_fits_labels!=None:
        ax.set_xticklabels(data_fits_labels[1:])
    if ylabel!=None:
        ax.set_ylabel(ylabel)
        plt.tight_layout()
    if ylims is None:
        ax.set_ylim([y_min,y_max])
    else:
        ax.set_ylim([ylims[0],ylims[1]])        
#     return data_comparison,data_all
    if pval:    
        col_ctrl=data_all.columns.tolist()[0]
        col_tests=data_all.columns.tolist()[1:]
        for col_testi in range(len(col_tests)):
            col_test=col_tests[col_testi]
            pval,side=get_wilcoxon(data_all,col_ctrl,col_test,side='one',denan=False)
            side='' #stitch
            # print pval
            if stars:
                pval=pval2stars(pval,ns=ns,numeric=False)
            if ns and (pval>0.05):
                side=''
                pval=''
                result="%s\n%s" % (side,pval)
            else:
                result="%s\n%s" % (side,pval)
            # print result
            # print ax.get_ylim()[0]+(ax.get_ylim()[1]-ax.get_ylim()[0])*0.05
            ax.text(col_testi,ax.get_ylim()[0]+(ax.get_ylim()[1]-ax.get_ylim()[0])*0.05,
                    result,ha='center',color='b',
                    bbox=dict(facecolor='w', edgecolor='none', 
                    # boxstyle='round',
                    alpha=0.6,)
                    )
        # data_all.to_csv('test1.csv')
    if plot_fh!=None:
        #plt.tight_layout()
        plt.savefig(plot_fh,format='pdf')
        plt.clf();plt.close()
    return ax,data_comparison,data_all

def annotatesigni(ax,x1,x2,y_max,s,space=0,lift=None):
    if lift==None:
        y_max=(y_max+1)
    elif lift!=None:
        y_max=(y_max+1)+(lift-1)*4
    if x1>x2:
        tmp=x2
        x2=x1
        x1=tmp
    ax.text(np.mean([x1,x2]),y_max+2,s,
            horizontalalignment='center',verticalalignment='center')
    ax.plot([x1+space, x2-space], [y_max+1, y_max+1], 'k-', lw=2)
    ax.plot([x1+space, x1+space], [y_max+0.5, y_max+1], 'k-', lw=2)
    ax.plot([x2-space, x2-space], [y_max+0.5, y_max+1], 'k-', lw=2)
    return ax

def plot_data_comparison_multiviolin_arching_pvals(prj_dh,data_fits,col,
                                                   data_fiti_ctrl=0,aasORcds="aas",ns=True,numeric=False,
                                     data_fits_labels=None,ylabel=None,statest='wilcox',
                                     figsize=[4,3],
                                     plot_fh=None):
    data_fit_fhs=["%s/data_fit/%s/%s" % (prj_dh,aasORcds,s) for s in data_fits]

    for data_fit_fh in data_fit_fhs:
        data_fit=pd.read_csv(data_fit_fh)   
        if data_fit.index.name!="mutids":
            data_fit=data_fit.set_index("mutids")

        if data_fit_fhs.index(data_fit_fh)==0:
            data_comparison=data_fit
        else:
            data_comparison=pd.concat([data_comparison.loc[:,col],data_fit.loc[:,col]],axis=1)

    data_comparison.columns=data_fits    

    data_comparison=data_comparison.unstack().reset_index()
    data_comparison.columns=["condi","mutids",col]
    y_max=data_comparison.loc[:,col].max()
    y_min=data_comparison.loc[:,col].min()

    data_fit_ctrl=data_fits[data_fiti_ctrl]
    data_fit_tests=[s for s in data_fits if data_fits.index(s)!=data_fiti_ctrl]

    # fig=
    plt.figure(figsize=figsize,dpi=300)
    ax=plt.subplot(111)
    import seaborn as sns
    from scipy.stats import mannwhitneyu,wilcoxon
#     plt.style.use('seaborn-whitegrid')
    plt.style.use('ggplot')
    sns.violinplot(x="condi", y=col, data=data_comparison,scale="width",ax=ax)
    for data_fit_test in data_fit_tests:
        data_fiti=data_fits.index(data_fit_test)    
        data_fiti_test=data_fit_tests.index(data_fit_test)
        if statest=='mann':
            z, pval = mannwhitneyu(data_comparison.set_index("condi").loc[data_fit_ctrl,col],
                                   data_comparison.set_index("condi").loc[data_fit_test,col],
                                   alternative='two-sided')
        elif statest=='wilcox':
            z, pval = wilcoxon(data_comparison.set_index("condi").loc[data_fit_ctrl,col],
                               data_comparison.set_index("condi").loc[data_fit_test,col],
#                                alternative='two-sided'
                              )
        if data_fiti_ctrl==0:
            ax=annotatesigni(ax,data_fiti_ctrl,data_fiti,y_max,pval2stars(pval,ns=ns,numeric=numeric),space=0.02,lift=data_fiti)    
        else:
            ax=annotatesigni(ax,data_fiti_ctrl,data_fiti,y_max,pval2stars(pval,ns=ns,numeric=numeric),space=0.02)                
    if data_fiti_ctrl!=0:
        ax.set_ylim([y_min-2,y_max+5])
    else:
        ax.set_ylim([y_min-2,y_max+(data_fiti)*5])
    ax.set_xlabel("")
    if data_fits_labels!=None:
        ax.set_xticklabels(data_fits_labels)
    if ylabel!=None:
        ax.set_ylabel(ylabel)
        plt.tight_layout()
    if plot_fh!=None:
        plt.savefig(plot_fh,format='pdf')
        plt.clf();plt.close()
    return ax
        
def plot_pie(data_comparison,col,col_count,explodei=None,
            colors=['yellowgreen', 'gold','lightgray'],
            fontsize=14,
             label=True,
             title=None,
            figsize=[2.1,2.1],
            plot_fh=None,
            legend=False,legend_save=False,
            ):
    counts=data_comparison.groupby(col).count().loc[:,col_count]
    counts=counts.sort_index()
    fig=plt.figure(figsize=[2.1,2.1],dpi=300)
    ax=plt.subplot(111)
    if explodei==0:
        explode=[0.2,0,0]
    elif explodei==1:
        explode=[0,0.2,0]        
    elif explodei==2:
        explode=[0,0,0.2] 
    elif explodei is None:
        explode=[0,0,0]
    elif explodei=='max':
        idxmax=pd.DataFrame(counts).reset_index().loc[:,'mutids'].idxmax()
        # print counts
        # print pd.DataFrame(counts).reset_index()
        # print idxmax
        explode=[0,0,0]
        explode[idxmax]=0.2
        # print explode
    elif explodei=='mid':
        idxmax=pd.DataFrame(counts).reset_index().loc[:,'mutids'].idxmax()
        idxmin=pd.DataFrame(counts).reset_index().loc[:,'mutids'].idxmin()
        # print counts
        # print pd.DataFrame(counts).reset_index()
        # print idxmax
        explode=[0.2,0.2,0.2]
        explode[idxmax]=0
        explode[idxmin]=0
        # print explode
    if label:
        labels=pd.DataFrame(counts).index.tolist()
    else:
        labels=['' for i in pd.DataFrame(counts).index.tolist()]
    patches, texts, autotexts = ax.pie(list(counts), explode=explode, 
                                       labels=labels, 
                                        colors=colors,
#                                             pctdistance=1,
                                       autopct='%1.1f%%', shadow=True, startangle=0)
    for text in texts:
        text.set_fontsize(fontsize)
    for text in autotexts:
        text.set_fontsize(fontsize)
        text.set_color('k')            
    if title!=None:
        ax.set_title(title,fontsize=20)
    if legend:
        ax2=ax.legend(bbox_to_anchor=(2, 1), loc=2, borderaxespad=0.)
    ax.axis('equal')
    if plot_fh!=None:
        fig.savefig(plot_fh,format='pdf',transparent=True)
        fig.savefig(plot_fh+'.png',format='png',transparent=True)
        if legend_save:
#                 fig=plt.figure()
#                 ax = plt.subplot()  #create the axes 
            ax.set_axis_off()  #turn off the axis 
            ax.legend()  #legend alone in the figure ,, labels
            ax.savefig("%s.legends.pdf" % plot_fh,
                       format='pdf',
                      transparent=True)
            ax.savefig("%s.legends.png" % plot_fh,
                       format='png',
                      transparent=True)
    return ax,counts

def plot_data_fit_dfe(data_fit,norm_type=None,col_fit="FiA",
                      bins=100,
                      annot_X=False,annot_syn=False,
                      xlabel=r'$F_{i}$',
                      axvspan_min=0,axvspan_max=0,axvspan_alpha=0.5,
                      plot_fh=None):
    """
    This plots histogram of Distribution of Fitness Effects (DFE).

    :param data_fit: fitness data (`data_fit`).
    :param norm_type: Type of normalization across samples [wild: wrt wild type | syn : wrt synonymous mutations | none : fold change serves as fitness]
    """
    plt.style.use('seaborn-white')
    fig = plt.figure(figsize=(6, 2.25),dpi=300)
    ax=plt.subplot(111)
    if norm_type=="syn":
        if not 'FiS' in data_fit.columns.tolist():
                data_fit.loc[:,'FiS']=data_fit.loc[(data_fit.loc[:,'ref']==data_fit.loc[:,'mut']),col_fit]

        data_fit[[col_fit,'FiS']].plot(kind='hist',bins=bins,color=['limegreen','gold'],
                                       edgecolor='k',
                                     ax=ax,zorder=3)
        l2=ax.legend(['Non-synonymous\nmutations','Synonymous\nmutations'],loc="upper right",
                    frameon=True)
#         elif norm_type=='syn':
#             ax.legend(['Non-synonymous\nmutations','Synonymous\nmutations'],loc="upper right",frameon=True)

    else:
        data_fit[col_fit].plot(kind='hist',bins=bins,
                               color='limegreen',
                               edgecolor='k',
                               ax=ax,zorder=3,alpha=0.75)    
    xlim=np.ceil(np.max([data_fit.loc[:,col_fit].max(),data_fit.loc[:,col_fit].min()*-1]))
    ax.axvspan(-xlim, axvspan_min, color='blue', alpha=axvspan_alpha,zorder=-1)
#     ax.axvspan(axvspan_min, axvspan_max, color='grey', alpha=0.05)
    ax.axvspan(axvspan_max, xlim, color='red', alpha=axvspan_alpha,zorder=-1)
    # l1=ax.legend(['Deleterious','Neutral','Beneficial'], loc='upper left')

    ymin,ymax=ax.get_ylim()

    if annot_X:
        data_fit_X=data_fit.loc[data_fit.loc[:,"mut"]=="X",col_fit]
        print data_fit.loc[(data_fit.loc[:,"mut"]=="X") & (data_fit.loc[:,"FiA"]>0),:]
        for i in list(data_fit_X):
            ax.axvline(x=i, ymin=ymin, ymax=ymax,color="k",zorder=0)

    if annot_syn:
        ax.axvline(x=0, ymin=ymin, ymax=ymax,color="gray",zorder=1)

    if annot_X:
        ax.legend(['Mutation to\nstop codon'],loc="upper right",frameon=True)
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Count')
    ax.set_xlim(-xlim,xlim)
    plt.tight_layout()
    if plot_fh!=None:
        plt.savefig(plot_fh,format='pdf')
        plt.clf();plt.close()
    return ax
