from __future__ import division
from __future__ import print_function
import sys
import time
import os
import click
import numpy as np
#import ipdb as pdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from EPIC import common

def monitor_each_parameter(wdirn, tex, parnames, nparams, bar=None, UseTex=False, png=False):

    yaxis1_color = 'C0'
    yaxis2_color = 'C4'

    list_of_k = np.loadtxt(os.path.join(wdirn, 'monitor_convergence.txt'), unpack=True)[0]
    hatR_V_W_pars = [np.loadtxt(os.path.join(wdirn, 'monitor_par%i.txt' % i), unpack=True) for i in range(nparams)]

    fig, axes = plt.subplots(nparams, 1, sharex='col')
    if nparams == 1:
        axes = [axes,]
    fig.set_size_inches(2*2, 2*nparams/2)
    for i, par in enumerate(parnames):
        axes[i].plot(list_of_k, hatR_V_W_pars[i][0,:] - 1, lw=1.0, ls='-', label=r'$' + tex[par] + '$', color=yaxis1_color)
        #axes[i].set_ylabel(r'$\hat{R}^{' + tex[par] + '}(k)-1$')
        axes[i].legend(loc='upper right', frameon=False, handlelength=0)
        sec_axis = axes[i].twinx()
        sec_axis.plot(list_of_k, hatR_V_W_pars[i][1,:], lw=0.5, ls='-', color=yaxis2_color)
        sec_axis.plot(list_of_k, hatR_V_W_pars[i][2,:], lw=0.5, ls=':', color=yaxis2_color)
        sec_axis.set_yscale('log')
        axes[i].set_yscale('log')
        # set color of yaxes 
        plt.setp(sec_axis.spines['right'], color=yaxis2_color)
        plt.setp(sec_axis.yaxis.get_majorticklines(), color=yaxis2_color)
        plt.setp(sec_axis.yaxis.get_minorticklines(), color=yaxis2_color)
        plt.setp(sec_axis.spines['left'], color=yaxis1_color) # (sec_axis is drawn above ax_R[i])
        plt.setp(axes[i].yaxis.get_majorticklines(), color=yaxis1_color)
        plt.setp(axes[i].yaxis.get_minorticklines(), color=yaxis1_color)
        if bar:
            bar.update(1)
    axes[-1].set_xlabel(r'$k$')
    if UseTex:
        axes[0].set_xlabel(r'$\hat{R}^p-1$ \qquad \qquad \qquad \qquad \quad $|\hat{V}(k)|$, $|W(k)|$')
    else:
        axes[0].set_xlabel(r'$\hat{R}^p-1$                                             $|\hat{V}(k)|$, $|W(k)|$')
    axes[0].xaxis.set_label_position('top')
    fig.tight_layout()
    fig.subplots_adjust(hspace=0)
    fig.savefig(os.path.join(wdirn, 'monitor_each_parameter_%i.pdf' % list_of_k[-1]))
    if png:
        fig.savefig(os.path.join(wdirn, 'monitor_each_parameter_%i.png' % list_of_k[-1]))


#===============================================================================


def plot_monitor_convergence(listwdirn, UseTex=False, png=False):

    fig, ax_R = plt.subplots(len(listwdirn), 1, sharex='col')
    if len(listwdirn) == 1:
        ax_R = [ax_R,]
    fig.set_size_inches(0.8*5, 0.8*2*len(listwdirn))

    yaxis1_color = 'C0'
    yaxis2_color = 'C4'

    for i, wdirn in enumerate(listwdirn):
        list_of_k, hatRp_of_k, V_of_k, W_of_k = np.loadtxt(os.path.join(wdirn, 'monitor_convergence.txt'), unpack=True)
        modelname = common.read_model_name(os.path.join(wdirn, '..'))

        ax_R[i].plot(list_of_k, hatRp_of_k-1, lw=1.0, color=yaxis1_color, label=modelname)
        ax_VW = ax_R[i].twinx()
        ax_VW.plot(list_of_k, V_of_k, lw=0.5, ls='-', color=yaxis2_color)#, label=r'$|\hat{V}(k)|$')
        ax_VW.plot(list_of_k, W_of_k, lw=0.5, ls=':', color=yaxis2_color)#, label=r'$|W(k)|$')
        ax_VW.set_yscale('log')
        ax_R[i].set_yscale('log')
        #plt.setp(ax_VW.get_yticklines(), color=yaxis2_color)
        # set color of yaxes 
        plt.setp(ax_VW.spines['right'], color=yaxis2_color)
        plt.setp(ax_VW.yaxis.get_majorticklines(), color=yaxis2_color)
        plt.setp(ax_VW.yaxis.get_minorticklines(), color=yaxis2_color)
        plt.setp(ax_VW.spines['left'], color=yaxis1_color) # (ax_VW is drawn above ax_R[i])
        plt.setp(ax_R[i].yaxis.get_majorticklines(), color=yaxis1_color)
        plt.setp(ax_R[i].yaxis.get_minorticklines(), color=yaxis1_color)
        ax_R[i].legend(loc="upper right", frameon=False, borderaxespad=0.5, handlelength=0)

    if UseTex:
        ax_R[0].set_xlabel(r'$\hat{R}^p(k)-1$ \qquad \qquad \qquad \qquad \quad $|\hat{V}(k)|$, $|W(k)|$', fontsize=12)
    else:
        ax_R[0].set_xlabel(r'$\hat{R}^p(k)-1$                                     $|\hat{V}(k)|$, $|W(k)|$', fontsize=12)
    ax_R[0].xaxis.set_label_position('top')
    ax_R[-1].set_xlabel(r'$k$')

    fig.tight_layout()
    # uses the last list_of_k from loop above 
    fig.subplots_adjust(hspace=0)
    fig.savefig(os.path.join(listwdirn[-1], 'monitor_convergence_%i.pdf' % list_of_k[-1]))
    if png:
        fig.savefig(os.path.join(listwdirn[-1], 'monitor_convergence_%i.png' % list_of_k[-1]))

    return listwdirn

if __name__ == '__main__':
    args = sys.argv

    png = common.lookarg('png', sys.argv)

    UseTex = common.lookarg('usetex', sys.argv)

    cfont = common.lookarg1('font=', sys.argv) or 'cmr10'

    if UseTex:
        plt.rc('font',**{'family':'serif','serif':[cfont]}) # 'Times'
        tex_packages = [
                r'\usepackage{amsmath}',
                ]
        if cfont == 'Times':
            tex_packages.append(r'\usepackage{txfontsb}')
            #tex_packages.append(r'\usepackage{mathptmx}')
        plt.rcParams['text.latex.preamble'] = tex_packages
        plt.rc('text', usetex=True)

    plt.rcParams['axes.linewidth'] = 0.5
    #plt.rcParams['text.latex.unicode'] = True
    #plt.rcParams['font.serif'] = 'Palatino'
    #plt.rcParams['legend.fontsize'] = 'medium'
    plt.rcParams['xtick.top'] = True
    plt.rcParams['ytick.right'] = True
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.major.width'] = 0.5
    plt.rcParams['ytick.major.width'] = 0.5

    listworkingdir = [arg for arg in args if os.path.isdir(arg)]
    npars = common.load_chains_and_model_details(os.path.join(listworkingdir[0], '..'))[5]

    itime = time.time()

    plotting_individual_parameters = common.fixed_length('Plotting variances and ratio for each parameter...')
    #pdb.set_trace()
    with click.progressbar(length=npars, show_pos=len(listworkingdir) == 1, empty_char='.', width=10, label=plotting_individual_parameters, info_sep='  |  ', show_eta=False) as bar:
        for wdirn in listworkingdir:
            _, _, _, tex, parnames, nparams, _ = common.load_chains_and_model_details(os.path.join(wdirn, '..'))
            monitor_each_parameter(wdirn, tex, parnames, nparams, bar=bar, UseTex=UseTex, png=png)

    listworkingdir = plot_monitor_convergence(listworkingdir, UseTex=UseTex, png=png)

    ftime = time.time()
    print('Total time: %s' % common.printtime(ftime - itime))
    print('')

