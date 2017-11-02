import os
import tempfile
import numpy as np
from scipy import sparse
import strpy.bobo.util
from strpy.bobo.util import tempcsv, temppdf,  islist, tolist, Stopwatch, lower_bound, quietprint, readcsv, writecsv
import strpy.bobo.metrics
from strpy.janus.dataset.cs2 import CS2
from itertools import product, groupby
from strpy.janus.openbr import readbee, writebee, brMaskMatrix, brSimilarityMatrix, openbr_eval, openbr_plot, importbr
import  sklearn.metrics
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from collections import OrderedDict
from strpy.bobo.geometry import BoundingBox

def set_fontsize(fontsize, fig=None):
    if fig is not None:
        plt.figure(fig)
        ax = plt.gca()
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(fontsize)

def decision_error_tradeoff(gtMatrix, simMatrix):
    """FNIR (eq.3) vs. FPIR (eq.1) in http://biometrics.nist.gov/cs_links/face/frvt/frvt2013/NIST_8009.pdf"""

    n_matesearch = gtMatrix.shape[0]

    # FPIR: At a given threshold t, the false alarm rate (i.e., the false positive identification rate (FPIR), or the type I error rate) measures what fraction
    # of comparisons between probe templates and non-mate gallery templates result in a match score exceeding t.
    (Yneg, Yhat) = (1.0-gtMatrix.flatten(), simMatrix.flatten())  # Yneg = non-mate gallery templates (true negatives)
    fpir = np.cumsum(Yneg[np.argsort(Yhat)]) / np.sum(Yneg.flatten());
    return fpir

    #fpir = [np.mean(np.float32(Y[k_nonmate] == np.float32(Yhat[k_nonmate] > t))) for t in T]

    # FNIR: The miss rate (i.e., the false negative identification rate (FNIR), or the type II error rate) measures what fraction of probe
    # searches will fail to match a mated gallery template above a score of t.
    (k_nonmate, Y, Yhat) = (np.argwhere(gtMatrix.flatten() == 0), gtMatrix.flatten(), simMatrix.flatten())

    T = np.sort(np.unique(Yhat.flatten()))  # ascending
    #fnir = [np.mean(np.sum(Y
    fnir = np.cumsum(Y[np.argsort(Yhat)]) / n_probe

    return (fnir, fpir)


def fnmr_at_fmr(y, yhat, at):
    """false negative match rate (FNMR) at false match rate (FMR)"""
    (fmr, fnmr) = det11(y, yhat)
    f = interp1d(fmr, fnmr)
    return f(at)

def fmr_at_fnmr(y, yhat, at):
    """false negative match rate (FNMR) at false match rate (FMR)"""
    (fmr, fnmr) = det11(y, yhat)
    f = interp1d(fnmr, fmr)
    return f(at)


def det11(y, yhat):
    """ False negative match rate (FNMR)=1-TAR, vs false match rate (FMR) """
    (far, tar, thresholds) = sklearn.metrics.roc_curve(y, yhat, pos_label=1)
    (fmr, fnmr) = (far, 1-tar)
    return (fmr, fnmr)

def tpir_at_fpir(y, yhat, at, topk=20):
    """true positive identification rate at false positive identification rate"""
    (fpir, tpir) = det1N(y, yhat, False, topk)
    f = interp1d(fpir, tpir)
    return f(at)

def fnir_at_fpir(y, yhat, at, topk=20):
    """true positive identification rate at false positive identification rate"""
    (fpir, tpir) = det1N(y, yhat, False, topk)
    f = interp1d(fpir, (1-tpir))
    return f(at)

def det1N(y, yhat, returnThresholds=False, topk=20):
    """ False negative identification rate (FNIR)=1-TPIR, vs false positive identification rate (FPIR) """
    i_nonmated = np.argwhere(np.sum(y, axis=1) == 0)  # WARNING: this assumes that the matrices use the open set gallery with non-mates
    i_mated = np.argwhere(np.sum(y, axis=1) > 0)

    (y_nonmated, yhat_nonmated) = (np.zeros( (len(i_nonmated), topk) ), np.zeros( (len(i_nonmated), topk) ))
    for (k,i) in enumerate(i_nonmated):
        j = np.argsort(-yhat[i,:]).flatten()  # yhat is similarity -> -yhat is distance -> sort in ascending distance order
        y_nonmated[k,:] = y[i,j[0:topk]]  # top-k only
        yhat_nonmated[k,:] = yhat[i,j[0:topk]]  # top-k only

    (y_mated, yhat_mated) = (np.zeros( (len(i_mated), topk) ), np.zeros( (len(i_mated), topk) ))
    for (k,i) in enumerate(i_mated):
        j = np.argsort(-yhat[i,:]).flatten()  # yhat is similarity -> -yhat is distance -> sort in ascending distance order
        y_mated[k,:] = y[i,j[0:topk]]  # top-k only
        yhat_mated[k,:] = yhat[i,j[0:topk]]  # top-k only

    yhatmax_nonmated = np.max(yhat_nonmated, axis=1).flatten()  # maximum nonmated similarity
    yhatmax_mated = np.zeros(y_mated.shape[0])

    for i in range(y_mated.shape[0]):
        k = np.argwhere(y_mated[i,:].flatten() > 0).flatten()
        if len(k) > 0:  # mate in top-k?
            yhatmax_mated[i] = yhat_mated[i, k]  # yes, mated similarity within top-k
        else:
            yhatmax_mated[i] = -np.inf  # no match in top-k

    thresholds = sorted(list(set(np.array(yhatmax_mated.flatten().tolist() + yhatmax_nonmated.flatten().tolist()).tolist())))  # smallest to largest similarity
    thresholds = [t for t in thresholds if np.isfinite(t)]

    tpir = np.zeros(len(thresholds))
    fpir = np.zeros(len(thresholds))
    fnir = np.zeros(len(thresholds))
    for (k,t) in enumerate(thresholds):
        #tpir[k] = np.mean(yhatmax_mated >= t) # mated similarity at or above threshold, tpir=1-fnir
        fnir[k] = np.mean(yhatmax_mated < t) # mated similarity not in top-k (-inf) or below threshold, tpir=1-fnir
        fpir[k] = np.mean(yhatmax_nonmated >= t)   # non-mated similarity at or above threshold

    #return (fpir.flatten(), tpir.flatten())
    if not returnThresholds:
        return (fpir.flatten(), (1-fnir).flatten())
    else: 
        return (fpir.flatten(), (1-fnir).flatten(), thresholds)



def plot_det1N(fpir=None, tpir=None, y=None, yhat=None, label=None, title=None, outfile=None, figure=None, hold=False, logx=True, style=None, fontsize=None, xlabel='False Match Rate (FMR)', ylabel='False Negative Match Rate (FNMR)', legendSwap=False, errorbars=None, color=None):
    return plot_det11(fnmr=(1-tpir), fmr=fpir, label=label, title=title, outfile=outfile, figure=figure, hold=hold, logx=logx, style=style, fontsize=fontsize, xlabel='False Positive Identification Rate (FPIR)', ylabel='False Negative Identification Rate (FNIR)', legendSwap=legendSwap, errorbars=errorbars, color=color)

def plot_det11(fnmr=None, fmr=None, y=None, yhat=None, label=None, title=None, outfile=None, figure=None, hold=False, logx=True, style=None, fontsize=None, xlabel='False Match Rate (FMR)', ylabel='False Negative Match Rate (FNMR)', legendSwap=False, errorbars=None, color=None):
    """ Plot DET 1:1 curves """
    if (fnmr is None) and (fmr is None):
        if y is not None and yhat is not None:
            (fmr, fnmr) = det11(y, yhat)
        else:
            raise ValueError()

    if figure is not None:
        plt.figure(figure)
        plt.hold(True)
    else:
        plt.figure()

    if hold == True:
        plt.hold(True)
    else:
        plt.clf()

    if style is None:
        # Use plot defaults to increment plot style when holding
        p = plt.plot(fmr, fnmr, label=label, color=color)
    else:
        p = plt.plot(fmr, fnmr, style, label=label, color=color)

    if errorbars is not None:
        (x,y,yerr) = zip(*errorbars)  # [(x,y,yerr), (x,y,yerr), ...]
        plt.gca().errorbar(x, y, yerr=yerr, fmt='none', ecolor=plt.getp(p[0], 'color'))  # HACK: force error bars to have same color as plot

    if logx == False:
        plt.plot([0, 1], [0, 1], 'k--', label="_nolegend_")
    if logx is True:
        plt.xscale('log')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    legendLoc = "upper right" if legendSwap else "lower left"
    if fontsize is None:
        plt.legend(loc=legendLoc)
    else:
        plt.legend(loc=legendLoc, prop={'size':fontsize})
    plt.grid(True)
    plt.gca().set_aspect('equal')
    plt.autoscale(tight=True)

    if title is not None:
        plt.title(title)

    # Font size
    ax = plt.gca()
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(fontsize)
    #plt.tight_layout()  # throws exception on macos
    plt.gcf().set_tight_layout(True)


    if outfile is not None:
        quietprint('[janus.metric.plot_det11]: saving "%s"' % outfile)
        plt.savefig(outfile)
    else:
        plt.show()


def ijba11(Y, Yh, verbose=True, prependToLegend='Split', fontsize=12, detPlotStyle=None, hold=False, detLegendSwap=False, figure=2, splitmean=False, verboseLegend=True):
    """IJB-A 1:1 evaluation for a list of splits containing pairwise similarity (Yh), and ground truth (Y)"""
    """ False negative match rate (FNMR) is 1-TAR, and FMR is equivalent to FAR """
    """ equations are defined in NIST report 14SEP15 """

    # Figure setup
    if hold is False:
        strpy.bobo.metrics.clearfig(figure)

    # Input normalization
    if islist(Y) == False and islist(Yh) == False:
        (Y, Yh) = ([Y], [Yh])  # Handle singleton splits

    # Evaluation over splits
    n_splits = len(Y)
    (fnmr_at_fmr_1Em3, fnmr_at_fmr_1Em2, far_at_tar_85, far_at_tar_95, fnmr_at_fmr_1Em1, fmr_fnmr) = ([], [], [], [], [], [])
    (fnmr_at_fmr_1Em6, fnmr_at_fmr_1Em5, fnmr_at_fmr_1Em4) = ([], [], [])
    for k in range(0, n_splits):
        # Verification: 1 to 1
        y = np.array(Y[k]).astype(np.float32).flatten()
        yhat = np.array(Yh[k]).astype(np.float32).flatten()
        fnmr_at_fmr_1Em6.append(fnmr_at_fmr(y, yhat, at=1E-6))
        fnmr_at_fmr_1Em5.append(fnmr_at_fmr(y, yhat, at=1E-5))
        fnmr_at_fmr_1Em4.append(fnmr_at_fmr(y, yhat, at=1E-4))
        fnmr_at_fmr_1Em3.append(fnmr_at_fmr(y, yhat, at=1E-3))
        fnmr_at_fmr_1Em2.append(fnmr_at_fmr(y, yhat, at=1E-2))
        fnmr_at_fmr_1Em1.append(fnmr_at_fmr(y, yhat, at=1E-1))
        far_at_tar_85.append(fmr_at_fnmr(y, yhat, at=(1-0.85)))
        far_at_tar_95.append(fmr_at_fnmr(y, yhat, at=(1-0.95)))
        if n_splits > 1:
            if verboseLegend:
                roc_label = '%s-%d [FNMR@FMR(1E-2)=%1.2f]' % (prependToLegend, int(k+1), fnmr_at_fmr_1Em2[k])
            else:
                roc_label = '%s-%d' % (prependToLegend, int(k+1))
        else:
            if verboseLegend:
                roc_label = '%s [FNMR@FMR(1E-2)=%1.2f]' % (prependToLegend, fnmr_at_fmr_1Em2[k])
            else:
                roc_label = '%s' % (prependToLegend)

        # Plot each split?
        if not splitmean:
            plot_det11(y=y, yhat=yhat, figure=figure, label=roc_label, style=detPlotStyle, logx=True, fontsize=fontsize, legendSwap=detLegendSwap, hold=True)
        fmr_fnmr.append(det11(y, yhat))

    # Results summary
    results = {'FNMR@FMR(1E-6)':{'mean':np.mean(fnmr_at_fmr_1Em6), 'std':np.std(fnmr_at_fmr_1Em6)},
               'FNMR@FMR(1E-5)':{'mean':np.mean(fnmr_at_fmr_1Em5), 'std':np.std(fnmr_at_fmr_1Em5)},
               'FNMR@FMR(1E-4)':{'mean':np.mean(fnmr_at_fmr_1Em4), 'std':np.std(fnmr_at_fmr_1Em4)},
               'FNMR@FMR(1E-3)':{'mean':np.mean(fnmr_at_fmr_1Em3), 'std':np.std(fnmr_at_fmr_1Em3)},
               'FNMR@FMR(1E-2)':{'mean':np.mean(fnmr_at_fmr_1Em2), 'std':np.std(fnmr_at_fmr_1Em2)},
               'FNMR@FMR(1E-1)':{'mean':np.mean(fnmr_at_fmr_1Em1), 'std':np.std(fnmr_at_fmr_1Em1)},
               'FAR@TAR(0.85)':{'mean':np.mean(far_at_tar_85), 'std':np.std(far_at_tar_85)},
               'FAR@TAR(0.95)':{'mean':np.mean(far_at_tar_95), 'std':np.std(far_at_tar_95)},
               'Y':Y, 'Yhat':Yh, 'fmr_fnmr':fmr_fnmr} # data to reproduce

    # Plot mean over splits?
    if splitmean:
        (minfmr, maxfmr, lenfmr) = (np.min([np.min(x[0]) for x in results['fmr_fnmr']]), np.max([np.max(x[0]) for x in results['fmr_fnmr']]), np.max([len(x[0]) for x in results['fmr_fnmr']]))
        fmr = np.arange(minfmr, maxfmr, (float(maxfmr)-float(minfmr))/float(lenfmr))  # mean interpolation
        fnmr = []
        for (x,y) in results['fmr_fnmr']:
            f = interp1d(x, y)
            fnmr.append([f(at) for at in fmr])
        fnmr = np.mean(fnmr, axis=0)
        if verboseLegend:
            det_label = '%s [FNMR@FMR(1E-2)=%1.2f]' % (prependToLegend, results['FNMR@FMR(1E-2)']['mean'])
        else:
            det_label = '%s' % (prependToLegend)
        errorbars = [(1E-3, results['FNMR@FMR(1E-3)']['mean'], results['FNMR@FMR(1E-3)']['std']), (1E-2, results['FNMR@FMR(1E-2)']['mean'], results['FNMR@FMR(1E-2)']['std']), (1E-1, results['FNMR@FMR(1E-1)']['mean'], results['FNMR@FMR(1E-1)']['std'])]
        plot_det11(fmr=fmr, fnmr=fnmr, figure=figure, label=det_label, style=detPlotStyle, logx=True, fontsize=fontsize, legendSwap=detLegendSwap, hold=True, errorbars=errorbars)
        (results['meanfmr'],  results['meanfnmr'],  results['maxfnmr'])  = (fmr, fnmr, np.nanmax(fnmr))

    # Print!
    results['DET'] = strpy.bobo.metrics.savefig(temppdf(), figure=figure)
    if verbose == True:
        if n_splits > 1:
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-6) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-6)']['mean'], results['FNMR@FMR(1E-6)']['std'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-5) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-5)']['mean'], results['FNMR@FMR(1E-5)']['std'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-4) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-4)']['mean'], results['FNMR@FMR(1E-4)']['std'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-3) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-3)']['mean'], results['FNMR@FMR(1E-3)']['std'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-2) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-2)']['mean'], results['FNMR@FMR(1E-2)']['std'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-1) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-1)']['mean'], results['FNMR@FMR(1E-1)']['std'])
            print '[janus.metrics.ijba11]: FAR@TAR(0.85) mean=%1.6f, std=%1.6f' % (results['FAR@TAR(0.85)']['mean'], results['FAR@TAR(0.85)']['std'])
            print '[janus.metrics.ijba11]: FAR@TAR(0.95) mean=%1.6f, std=%1.6f' % (results['FAR@TAR(0.95)']['mean'], results['FAR@TAR(0.95)']['std'])
        else:
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-6)=%1.6f' % (results['FNMR@FMR(1E-6)']['mean'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-5)=%1.6f' % (results['FNMR@FMR(1E-5)']['mean'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-4)=%1.6f' % (results['FNMR@FMR(1E-4)']['mean'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-3)=%1.6f' % (results['FNMR@FMR(1E-3)']['mean'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-2)=%1.6f' % (results['FNMR@FMR(1E-2)']['mean'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-1)=%1.6f' % (results['FNMR@FMR(1E-1)']['mean'])
            print '[janus.metrics.ijba11]: FAR@TAR(0.85)=%1.6f' % (results['FAR@TAR(0.85)']['mean'])
            print '[janus.metrics.ijba11]: FAR@TAR(0.95)=%1.6f' % (results['FAR@TAR(0.95)']['mean'])

        print '[janus.metrics.ijba11]: DET curve saved to "%s"' % results['DET']

    return results



def ijba1N(Y, Yh, verbose=True, prependToLegend='Split', fontsize=12, detPlotStyle=None, hold=False, detLegendSwap=False, cmcPlotStyle=None, cmcLegendSwap=None, cmcFigure=3, detFigure=4, splitmean=False, cmcLogy=False, L=20, verboseLegend=True, verboseLegendRank=10, cmcMinY=0.0, color=None, topk=20):
    """IJB-A 1:N evaluation"""

    # Figure setup
    if hold is False:
        strpy.bobo.metrics.clearfig(cmcFigure)
        strpy.bobo.metrics.clearfig(detFigure)

    # Input normalization
    if islist(Y) == False and islist(Yh) == False:
        (Y, Yh) = ([Y], [Yh])  # Handle singleton splits

    # Evaluation over splits
    n_splits = len(Y)
    (tpir_at_rank_1, tpir_at_rank_10, tpir_at_rank_20, tpir_at_fpir_1Em3, tpir_at_fpir_1Em2, fnir_at_fpir_3Em2, tpir_at_fpir_1Em1, recall_at_rank_all, fnir_at_fpir_all) = ([], [], [], [], [], [], [], [], [])
    tpir_at_rank_5 = []
    tpir_at_rank_dict = {1:tpir_at_rank_1, 5:tpir_at_rank_5, 10:tpir_at_rank_10, 20:tpir_at_rank_20}
    desired_legend_rank_val = tpir_at_rank_dict[verboseLegendRank] if verboseLegendRank in tpir_at_rank_dict else tpir_at_rank_10
    desired_legend_rank = verboseLegendRank if verboseLegendRank in tpir_at_rank_dict else 10
    for k in range(0, n_splits):
        # Cumulative match characteristic
        gtMatrix = Y[k].astype(np.float32)
        simMatrix = Yh[k].astype(np.float32)
        (rank, recall) = strpy.bobo.metrics.cumulative_match_characteristic(simMatrix, gtMatrix)
        tpir_at_rank_1.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=1))
        tpir_at_rank_5.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=5))
        tpir_at_rank_10.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=10))
        tpir_at_rank_20.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=20))
        if n_splits > 1:
            if verboseLegend:
                cmc_label = '%s-%d [TPIR@Rank%s=%1.2f]' % (prependToLegend, int(k+1),desired_legend_rank, desired_legend_rank_val[k])
            else:
                cmc_label = '%s-%d' % (prependToLegend, int(k+1))
        else:
            if verboseLegend:
                cmc_label = '%s [TPIR@Rank%s=%1.2f]' % (prependToLegend,desired_legend_rank, desired_legend_rank_val[k])
            else:
                cmc_label = '%s' % (prependToLegend)
        if not splitmean:
            strpy.bobo.metrics.plot_cmc(rank, recall, label=cmc_label, figure=cmcFigure, style=cmcPlotStyle, fontsize=fontsize, legendSwap=cmcLegendSwap, hold=True, logy=cmcLogy, miny=cmcMinY, color=color)

        # DET 1:N curve (top-L)
        (yh, y) = ([], [])
        for i in range(0, Yh[k].shape[0]):
            j = np.argsort(-Yh[k][i,:])  # yhat is similarity -> -yhat is distance -> sort in ascending distance order
            yh.append( [Yh[k][i,jj] for jj in j[0:L]] )
            y.append( [Y[k][i,jj] for jj in j[0:L]] )
        (fpir, tpir) = det1N(np.array(y), np.array(yh), returnThresholds=False, topk=topk)
#        (fpir, tpir) = det1N(Y[k], Yh[k])  # WARNING: this was used to generate results for 18DEC15 datacall, makes no difference

        fnir = 1-tpir

        tpir_at_fpir_1Em1.append(tpir_at_fpir(Y[k], Yh[k], at=1E-1, topk=topk))
        tpir_at_fpir_1Em2.append(tpir_at_fpir(Y[k], Yh[k], at=1E-2, topk=topk))
        tpir_at_fpir_1Em3.append(tpir_at_fpir(Y[k], Yh[k], at=1E-3, topk=topk))
        fnir_at_fpir_3Em2.append(fnir_at_fpir(Y[k], Yh[k], at=3E-2, topk=topk))

        if n_splits > 1:
            if verboseLegend:
                det_label = '%s-%d [FNIR@FPIR(1E-2)=%1.2f]' % (prependToLegend, int(k+1), 1-tpir_at_fpir_1Em2[k])
            else:
                det_label = '%s-%d' % (prependToLegend, int(k+1))
        else:
            if verboseLegend:
                det_label = '%s [FNIR@FPIR(1E-2)=%1.2f]' % (prependToLegend, 1-tpir_at_fpir_1Em2[k])
            else:
                det_label = '%s' % (prependToLegend)

        if not splitmean:
            plot_det1N(fpir=fpir, tpir=tpir, label=det_label, style=detPlotStyle, fontsize=fontsize, legendSwap=detLegendSwap, hold=True, figure=detFigure, color=color)
        recall_at_rank_all.append( (rank, recall) )
        fnir_at_fpir_all.append( (fpir, fnir) )

    # Results summary
    results = {'TPIR@Rank1':{'mean':np.mean(tpir_at_rank_1), 'std':np.std(tpir_at_rank_1)},
               'TPIR@Rank5':{'mean':np.mean(tpir_at_rank_5), 'std':np.std(tpir_at_rank_5)},
               'TPIR@Rank10':{'mean':np.mean(tpir_at_rank_10), 'std':np.std(tpir_at_rank_10)},
               'TPIR@Rank20':{'mean':np.mean(tpir_at_rank_20), 'std':np.std(tpir_at_rank_20)},
               'FNIR@FPIR(3E-2)':{'mean':np.mean(fnir_at_fpir_3Em2), 'std':np.std(fnir_at_fpir_3Em2)},
               'TPIR@FPIR(1E-3)':{'mean':np.mean(tpir_at_fpir_1Em3), 'std':np.std(tpir_at_fpir_1Em3)},
               'TPIR@FPIR(1E-2)':{'mean':np.mean(tpir_at_fpir_1Em2), 'std':np.std(tpir_at_fpir_1Em2)},
               'TPIR@FPIR(1E-1)':{'mean':np.mean(tpir_at_fpir_1Em1), 'std':np.std(tpir_at_fpir_1Em1)},
               'recall_at_rank':recall_at_rank_all, 'fnir_at_fpir':fnir_at_fpir_all}

    # Interpolated mean curves?
    if splitmean:
        # Mean CMC curve interpolated over splits
        (minrank, maxrank, lenrank) = (np.min([np.min(x[0]) for x in results['recall_at_rank']]), np.min([np.max(x[0]) for x in results['recall_at_rank']]), np.max([len(x[0]) for x in results['recall_at_rank']]))
        rank = np.arange(minrank, maxrank, (float(maxrank)-float(minrank))/(float(lenrank)))  # mean interpolation
        recall = []

        for (x,y) in results['recall_at_rank']:
            f = interp1d(x, y)
            recall.append([f(at) for at in rank])
        recall = np.mean(recall, axis=0)
        (results['meanrank'],  results['meanrecall'])  = (rank, recall)
        if verboseLegend:
            cmc_label = '%s [TPIR@Rank%s=%1.2f]' % (prependToLegend, desired_legend_rank, results['TPIR@Rank%s' % desired_legend_rank]['mean'])
        else:
            cmc_label = '%s' % (prependToLegend)
        errorbars = [(1, results['TPIR@Rank1']['mean'], results['TPIR@Rank1']['std']),
                     (5, results['TPIR@Rank5']['mean'], results['TPIR@Rank5']['std']),
                     (10, results['TPIR@Rank10']['mean'], results['TPIR@Rank10']['std'])]
        strpy.bobo.metrics.plot_cmc(rank, recall, label=cmc_label, figure=cmcFigure, style=cmcPlotStyle, fontsize=fontsize, legendSwap=cmcLegendSwap, hold=True, errorbars=errorbars, logy=cmcLogy, miny=cmcMinY, color=color)

        # Mean DET curve interpolated over splits
        # changing plot limits such that interpolation doesn't fall outside the range for some splits; One caveat will be that some splits will get clipped
        (minfpir, maxfpir, lenfpir) = (np.max([np.min(x[0]) for x in results['fnir_at_fpir']]), np.min([np.max(x[0]) for x in results['fnir_at_fpir']]), np.max([len(x[0]) for x in results['fnir_at_fpir']]))
        fpir = np.arange(minfpir, maxfpir, (float(maxfpir)-float(minfpir))/(float(lenfpir)))  # mean interpolation
        fnir = []
        for (x,y) in results['fnir_at_fpir']:
            f = interp1d(x, y)
            fnir.append([f(at) for at in fpir])
        fnir_mean = np.mean(fnir, axis=0)
        fnir_std = np.std(fnir, axis=0)
        f = interp1d(fpir, fnir_mean)
        g = interp1d(fpir, fnir_std)
        (results['meanfpir'],  results['meanfnir'])  = (fpir, fnir_mean)
        if verboseLegend:
            det_label = '%s [FNIR@FPIR(1E-2)=%1.2f]' % (prependToLegend, f(1E-2))
        else:
            det_label = '%s' % (prependToLegend)
        errorbars = [((1E-3), f(1E-3), g(1E-3)), ((1E-2), f(1E-2), g(1e-2)), (1E-1, f(1E-1), g(1E-1))]
        plot_det1N(fpir=fpir, tpir=(1.0-fnir_mean), label=det_label, style=detPlotStyle, fontsize=fontsize, legendSwap=detLegendSwap, hold=True, figure=detFigure, errorbars=errorbars, color=color)


    # Print!
    results['CMC'] = strpy.bobo.metrics.savefig(temppdf(), figure=cmcFigure)
    results['DET'] = strpy.bobo.metrics.savefig(temppdf(), figure=detFigure)

    if verbose == True:
        print '[janus.metrics.ijba1N]: TPIR@Rank1 mean=%1.3f, std=%1.3f' % (results['TPIR@Rank1']['mean'], results['TPIR@Rank1']['std'])
        print '[janus.metrics.ijba1N]: TPIR@Rank5 mean=%1.3f, std=%1.3f' % (results['TPIR@Rank5']['mean'], results['TPIR@Rank5']['std'])
        print '[janus.metrics.ijba1N]: TPIR@Rank10 mean=%1.3f, std=%1.3f' % (results['TPIR@Rank10']['mean'], results['TPIR@Rank10']['std'])
        print '[janus.metrics.ijba1N]: TPIR@Rank20 mean=%1.3f, std=%1.3f' % (results['TPIR@Rank20']['mean'], results['TPIR@Rank20']['std'])
        print '[janus.metrics.ijba1N]: TPIR@FPIR(1E-1) mean=%1.3f, std=%1.3f' % (results['TPIR@FPIR(1E-1)']['mean'], results['TPIR@FPIR(1E-1)']['std'])
        print '[janus.metrics.ijba1N]: FNIR@FPIR(3E-2) mean=%1.3f, std=%1.3f' % (results['FNIR@FPIR(3E-2)']['mean'], results['FNIR@FPIR(3E-2)']['std'])
        print '[janus.metrics.ijba1N]: TPIR@FPIR(1E-2) mean=%1.3f, std=%1.3f' % (results['TPIR@FPIR(1E-2)']['mean'], results['TPIR@FPIR(1E-2)']['std'])
        print '[janus.metrics.ijba1N]: CMC curve saved to "%s"' % results['CMC']
        print '[janus.metrics.ijba1N]: DET curve saved to "%s"' % results['DET']

    return results


def ijba(Y11, Yh11, Y1N, Yh1N, verbose=True, prependToLegend='Split', fontsize=12, rocPlotStyle=None, cmcPlotStyle=None, hold=False, rocLegendSwap=False, cmcLegendSwap=False):
    """Y/YHat is list of numpy arrays over splits of size NumProbe x NumGallery, or a vector which can be reshaped using N_gallery"""

    # Cleanup
    if hold is False:
        strpy.bobo.metrics.clearfig(1)
        strpy.bobo.metrics.clearfig(2)

    # Input normalization
    if islist(Y11) == False and islist(Yh11) == False:
        (Y11, Yh11, Y1N, Yh1N) = ([Y11], [Yh11], [Y1N], [Yh1N])  # Handle singleton splits

    # Evaluation over splits
    n_splits = len(Y11)
    (tar_at_far1Em3, tar_at_far1Em2, tar_at_far1Em1, tdr_at_rank1, tdr_at_rank5, tdr_at_rank10) = ([], [], [], [], [], [])
    for k in range(0, n_splits):
        # Verification: 1 to 1
        y = np.array(Y11[k]).astype(np.float32).flatten()
        yhat = np.array(Yh11[k]).astype(np.float32).flatten()
        tar_at_far1Em3.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-3))
        tar_at_far1Em2.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-2))
        tar_at_far1Em1.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-1))
        if n_splits > 1:
            roc_label = '%s-%d [TAR@FAR(1E-3)=%1.2f]' % (prependToLegend, int(k+1), tar_at_far1Em3[k])
        else:
            roc_label = '%s [TAR@FAR(1E-3)=%1.2f]' % (prependToLegend, tar_at_far1Em3[k])
        strpy.bobo.metrics.plot_roc(y, yhat, figure=2, label=roc_label, style=cmcPlotStyle, logx=True, fontsize=fontsize, legendSwap=rocLegendSwap, hold=True)

        # Identification
        gtMatrix = Y1N[k].astype(np.float32)
        simMatrix = Yh1N[k].astype(np.float32)
        (rank, recall) = strpy.bobo.metrics.cumulative_match_characteristic(simMatrix, gtMatrix)
        tdr_at_rank1.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=1))
        tdr_at_rank5.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=5))
        tdr_at_rank10.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=10))
        if n_splits > 1:
            cmc_label = '%s-%d [Recall@Rank5=%1.2f]' % (prependToLegend, int(k+1), tdr_at_rank5[k])
        else:
            cmc_label = '%s [Recall@Rank5=%1.2f]' % (prependToLegend, tdr_at_rank5[k])
        strpy.bobo.metrics.plot_cmc(rank, recall, label=cmc_label, figure=1, style=rocPlotStyle, fontsize=fontsize, legendSwap=cmcLegendSwap, hold=True)

        # DET


    # Results summary
    results = {'TAR@FAR(1E-3)':{'mean':np.mean(tar_at_far1Em3), 'std':np.std(tar_at_far1Em3)},
               'TAR@FAR(1E-2)':{'mean':np.mean(tar_at_far1Em2), 'std':np.std(tar_at_far1Em2)},
               'TAR@FAR(1E-1)':{'mean':np.mean(tar_at_far1Em1), 'std':np.std(tar_at_far1Em1)},
               'Recall@Rank1':{'mean':np.mean(tdr_at_rank1), 'std':np.std(tdr_at_rank1)},
               'Recall@Rank5':{'mean':np.mean(tdr_at_rank5), 'std':np.std(tdr_at_rank5)},
               'Recall@Rank10':{'mean':np.mean(tdr_at_rank10), 'std':np.std(tdr_at_rank10)},
               'ROC':strpy.bobo.metrics.savefig(temppdf(), figure=2),
               'CMC':strpy.bobo.metrics.savefig(temppdf(), figure=1)}

    # Print!
    if verbose == True:
        print '[janus.metrics.ijba]: TAR@FAR(1E-3) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-3)']['mean'], results['TAR@FAR(1E-3)']['std'])
        print '[janus.metrics.ijba]: TAR@FAR(1E-2) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-2)']['mean'], results['TAR@FAR(1E-2)']['std'])
        print '[janus.metrics.ijba]: TAR@FAR(1E-1) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-1)']['mean'], results['TAR@FAR(1E-1)']['std'])
        print '[janus.metrics.ijba]: Recall@Rank(1) mean=%1.3f, std=%1.3f' % (results['Recall@Rank1']['mean'], results['Recall@Rank1']['std'])
        print '[janus.metrics.ijba]: Recall@Rank(5) mean=%1.3f, std=%1.3f' % (results['Recall@Rank5']['mean'], results['Recall@Rank5']['std'])
        print '[janus.metrics.ijba]: Recall@Rank(10) mean=%1.3f, std=%1.3f' % (results['Recall@Rank10']['mean'], results['Recall@Rank10']['std'])
        print '[janus.metrics.ijba]: ROC curve saved to "%s"' % results['ROC']
        print '[janus.metrics.ijba]: CMC curve saved to "%s"' % results['CMC']

    # Done!
    return results





def report(Y, Yhat, N_gallery=None, verbose=True, prependToLegend='Split', atrank=[1,5,10], fontsize=12, rocPlotStyle=None, cmcPlotStyle=None, hold=False, rocLegendSwap=False, cmcLegendSwap=False, cmcLogy=False, verboseLegend=True, cmcMinY=0.0, display=True):
    """Y/YHat is list of numpy arrays over splits of size NumProbe x NumGallery, or a vector which can be reshaped using N_gallery"""

    # Cleanup
    if hold is False and display is True:
        strpy.bobo.metrics.clearfig(1)
        strpy.bobo.metrics.clearfig(2)

    # Input normalization
    if islist(Y) == False and islist(Yhat) == False:
        (Y, Yhat) = ([Y], [Yhat])  # Handle singleton splits for Y and Yhat

    # Evaluation over splits
    n_splits = len(Y)
    eer = []; fpr_at_tpr85 = []; fpr_at_tpr75 = []; tdr_at_rank1=[];  tdr_at_rank5=[]; tdr_at_rank10=[]; fpr_at_tpr75 = [];
    (tar_at_far1Em3, tar_at_far1Em2, tar_at_far1Em1) = ([], [], [])
    for k in range(0, n_splits):
        y = np.array(Y[k]).astype(np.float32).flatten()
        yhat = np.array(Yhat[k]).astype(np.float32).flatten()
        n_gallery = N_gallery[k] if N_gallery is not None else Y[k].shape[1]

        # Verification
        eer.append(np.floor(100*strpy.bobo.metrics.roc_eer(y, yhat)) / (100.0))
        fpr_at_tpr75.append(strpy.bobo.metrics.fpr_at_tpr(y, yhat, at=0.75))
        fpr_at_tpr85.append(strpy.bobo.metrics.fpr_at_tpr(y, yhat, at=0.85))
        tar_at_far1Em3.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-3))
        tar_at_far1Em2.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-2))
        tar_at_far1Em1.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-1))

        # Identification
        gtMatrix = y.reshape( (len(y)/n_gallery, n_gallery) )
        simMatrix = yhat.reshape( (len(yhat)/n_gallery, n_gallery) )
        (rank, recall) = strpy.bobo.metrics.cumulative_match_characteristic(simMatrix, gtMatrix)
        tdr_at_rank1.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=atrank[0]))
        tdr_at_rank5.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=atrank[1]))
        tdr_at_rank10.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=atrank[2]))

        # Plots
        if n_splits > 1:
            if verboseLegend:
                cmc_label = '%s-%d [TDR@Rank%d=%1.3f]' % (prependToLegend, int(k+1), atrank[2], tdr_at_rank10[k])
            else:
                cmc_label = '%s-%d' % (prependToLegend, int(k+1))
        else:
            if verboseLegend:
                cmc_label = '%s [TDR@Rank%d=%1.3f]' % (prependToLegend, atrank[2], tdr_at_rank10[k])
            else:
                cmc_label = '%s' % (prependToLegend)
        if display:
            strpy.bobo.metrics.plot_cmc(rank, recall, label=cmc_label, figure=1, style=rocPlotStyle, fontsize=fontsize, legendSwap=cmcLegendSwap, hold=hold, logy=cmcLogy, miny=cmcMinY)

        # ROC plots
        if n_splits > 1:
            if verboseLegend:
                roc_label = '%s-%d [FPR@TDR(0.85)=%1.3f]' % (prependToLegend, int(k+1), fpr_at_tpr85[k])
            else:
                roc_label = '%s-%d' % (prependToLegend, int(k+1))
        else:
            if verboseLegend:
                roc_label = '%s [FPR@TDR(0.85)=%1.3f]' % (prependToLegend, fpr_at_tpr85[k])
            else:
                roc_label = '%s' % (prependToLegend)
        if display:
            strpy.bobo.metrics.plot_roc(y, yhat, figure=2, label=roc_label, style=cmcPlotStyle, logx=True, fontsize=fontsize, legendSwap=rocLegendSwap, hold=hold)

    # Results summary
    results = {'EER':{'mean':np.mean(eer), 'std':np.std(eer)},
               'FPR@TDR=0.75':{'mean':np.mean(fpr_at_tpr75), 'std':np.std(fpr_at_tpr75)},
               'FPR@TDR=0.85':{'mean':np.mean(fpr_at_tpr85), 'std':np.std(fpr_at_tpr85)},
               'TAR@FAR(1E-3)':{'mean':np.mean(tar_at_far1Em3), 'std':np.std(tar_at_far1Em3)},
               'TAR@FAR(1E-2)':{'mean':np.mean(tar_at_far1Em2), 'std':np.std(tar_at_far1Em2)},
               'TAR@FAR(1E-1)':{'mean':np.mean(tar_at_far1Em1), 'std':np.std(tar_at_far1Em1)},
               'ROC':strpy.bobo.metrics.savefig(temppdf(), figure=2) if display else None,
               'CMC':strpy.bobo.metrics.savefig(temppdf(), figure=1) if display else None,
               'TDR@Rank=%d' % atrank[0]:{'mean':np.mean(tdr_at_rank1), 'std':np.std(tdr_at_rank1)},
               'TDR@Rank=%d' % atrank[1]:{'mean':np.mean(tdr_at_rank5), 'std':np.std(tdr_at_rank5)},
               'TDR@Rank=%d' % atrank[2]:{'mean':np.mean(tdr_at_rank10), 'std':np.std(tdr_at_rank10)},
               'pickled':strpy.bobo.util.save( (Y,Yhat,N_gallery) )}

    # Print!
    if verbose == True:
        print '[janus.metrics.report]: EER mean=%1.3f, std=%1.3f' % (results['EER']['mean'], results['EER']['std'])
        print '[janus.metrics.report]: FPR@TDR=0.75 mean=%1.5f, std=%1.5f' % (results['FPR@TDR=0.75']['mean'], results['FPR@TDR=0.75']['std'])
        print '[janus.metrics.report]: FPR@TDR=0.85 mean=%1.5f, std=%1.5f' % (results['FPR@TDR=0.85']['mean'], results['FPR@TDR=0.85']['std'])
        print '[janus.metrics.report]: TAR@FAR(1E-3) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-3)']['mean'], results['TAR@FAR(1E-3)']['std'])
        print '[janus.metrics.report]: TAR@FAR(1E-2) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-2)']['mean'], results['TAR@FAR(1E-2)']['std'])
        print '[janus.metrics.report]: TAR@FAR(1E-1) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-1)']['mean'], results['TAR@FAR(1E-1)']['std'])
        print '[janus.metrics.report]: TDR@Rank%d mean=%1.3f, std=%1.3f' % (atrank[0], results['TDR@Rank=%d' % atrank[0]]['mean'], results['TDR@Rank=%d' % atrank[0]]['std'])
        print '[janus.metrics.report]: TDR@Rank%d mean=%1.3f, std=%1.3f' % (atrank[1], results['TDR@Rank=%d' % atrank[1]]['mean'], results['TDR@Rank=%d' % atrank[1]]['std'])
        print '[janus.metrics.report]: TDR@Rank%d mean=%1.3f, std=%1.3f' % (atrank[2], results['TDR@Rank=%d' % atrank[2]]['mean'], results['TDR@Rank=%d' % atrank[2]]['std'])
        print '[janus.metrics.report]: ROC curve saved to "%s"' % results['ROC']
        print '[janus.metrics.report]: CMC curve saved to "%s"' % results['CMC']
        print '[janus.metrics.report]: data to reproduce saved to "%s"' % results['pickled']

    # Done!
    return results

def asgallery(y, n_gallery):
    """Convert nx1 vector y to (n/m)xm Gallery Matrix, assume that y is stored row major"""
    ya = np.array(y);
    return ya.reshape( (ya.size/n_gallery, n_gallery) )



def detection_from_imscene(imscenedet, imscenetruth, min_overlap=0.2):
    """Return assigned detections"""

    y = []; yhat = [];
    for (j, (imdet, imtruth)) in enumerate(zip(imscenedet, imscenetruth)):
        print '[janus.metrics.detection][%d/%d]: detector evaluation' % (j+1, len(imscenedet))

        # Detector for current scene
        det = [{'bbox':im.boundingbox(), 'label':im.category(), 'probability':im.probability()} for im in imdet.objects()]
        truth = [{'bbox':im.boundingbox(), 'label':im.category(), 'probability':im.probability()} for im in imtruth.objects()]
        det = sorted(det, key=lambda x: x['probability'], reverse=True)  # sort inplace, descending by score

        # Assign detections
        is_assigned = [False]*len(truth)
        for d in det:
            overlap = [d['bbox'].overlap(t['bbox']) for t in truth]  # overlap of current detection with truth bounding boxes
            is_overlapped_label = [(x >= min_overlap) and (d['label'] == t['label']) for (x,t) in zip(overlap, truth)]  # minimum overlap and same label?
            if any(is_overlapped_label):  # any assignments with minimum overlap and same label?
                max_overlap = [k for (k,v) in enumerate(overlap) if (np.abs(v - max(overlap)) < 1E-6 and is_overlapped_label[k])]  # truth bounding box with maximum overlap
                if len(max_overlap) > 0 and is_assigned[max_overlap[0]] == False:  # truth already assigned?
                    # True detection!
                    y.append(1.0)
                    yhat.append(d['probability']) # true detection probability
                    is_assigned[max_overlap[0]] = True
                else:
                    #y.append( (0.0, -np.inf) )  # non-maximum suppression
                    pass  # ignore multiple detections for same truth
            else:
                # False alarm
                y.append(0.0)
                yhat.append(d['probability'])

        # Missed detections
        for t in is_assigned:
            if t == False:
                y.append(1.0)
                yhat.append(0.0)

    # Return ground truth label and detection score
    return (y, yhat)

def detection_from_csvfile(detcsvfile, truthcsvfile, min_overlap=0.2, ignore=False, skipheader=True):
    """Return {0,1} ground truth (Y) and similarity scores (Yh) for assigned detection suitable for computing ROC curve, using csv file inputs
       truth CSV files of the form (imagefile, xmin, ymin, width, height, ignore... )
       detector CSV files of the form (imagefile, xmin, ymin, width, height, confidence ... )
    """

    # Unique image filenames
    if skipheader:
        imfiles = list(set([x[0] for x in readcsv(detcsvfile)[1:]]))
        assert len(imfiles) == len(set([x[0] for x in readcsv(truthcsvfile)[1:]]))
    else:
        imfiles = list(set([x[0] for x in readcsv(detcsvfile)]))
        assert len(imfiles) == len(set([x[0] for x in readcsv(truthcsvfile)]))

    # group csv rows by filename into dictionary keyed by filename        
    d_detcsv = {key:list(group) for (key, group) in groupby(readcsv(detcsvfile), lambda x: x[0])}  
    d_truthcsv = {key:list(group) for (key, group) in groupby(readcsv(truthcsvfile), lambda x: x[0])}  

    # Greedy assignment
    y = []; yhat = [];    
    for (j, f) in enumerate(imfiles):
        if j % 1000 == 0:
            print '[janus.metrics.detection_from_csvfile][%d/%d]: detector evaluation "%s"' % (j+1, len(imfiles), f)

        # All detections in current image
        det = [{'bbox':BoundingBox(xmin=float(x[1]), ymin=float(x[2]), width=float(x[3]), height=float(x[4])), 'label':'object', 'probability':float(x[5])} for x in d_detcsv[f] if len(x[1])>0]
        truth = [{'bbox':BoundingBox(xmin=float(x[1]), ymin=float(x[2]), width=float(x[3]), height=float(x[4])), 'label':'object', 'probability':1.0, 'ignore':float(x[5])} for x in d_truthcsv[f] if len(x[1])>0]
        det = sorted(det, key=lambda x: x['probability'], reverse=True)  # sort inplace, descending by score

        # Assign detections
        is_assigned = [False]*len(truth)
        for d in det:
            overlap = [d['bbox'].overlap(t['bbox']) for t in truth]  # overlap of current detection with truth bounding boxes
            is_overlapped_label = [(x >= min_overlap) and (d['label'] == t['label']) for (x,t) in zip(overlap, truth)]  # minimum overlap and same label?
            if any(is_overlapped_label):  # any assignments with minimum overlap and same label?
                max_overlap = [k for (k,v) in enumerate(overlap) if (np.abs(v - max(overlap)) < 1E-6 and is_overlapped_label[k])]  # truth bounding box with maximum overlap
                if len(max_overlap) > 0 and is_assigned[max_overlap[0]] == False:  # truth already assigned?
                    # True detection!
                    y.append(1.0)
                    yhat.append(d['probability']) # true detection probability
                    is_assigned[max_overlap[0]] = True
                else:
                    #y.append( (0.0, -np.inf) )  # non-maximum suppression
                    pass  # ignore multiple detections for same truth
            else:
                # False alarm
                y.append(0.0)
                yhat.append(d['probability'])

        # Missed detections
        for t in is_assigned:
            if t == False:
                y.append(1.0)
                yhat.append(0.0)

    # Return ground truth label and detection score
    return (y, yhat)



#FIXME: Generalize to different datasets
def order_cs2_results(split, y, yhat, probe_ids, gallery_ids):
    ''' Returns ground truth, scores, probe and gallery template ids ordered according to the CS2 protocol csv files'''

    protocoldir = CS2().protocoldir

    num_y = len(y)
    num_yhat = len(yhat)
    assert num_y==num_yhat, 'num_y [%d] != num_yhat [%d]'%(num_y, num_yhat)
    num_id_pairs = len(probe_ids)
    assert num_y==num_id_pairs, 'num_y [%d] != num_id_pairs [%d]'%(num_y, num_id_pairs)

    probecsv  = os.path.join(protocoldir, 'split%d'%split, 'probe_%d.csv'%split)
    gallerycsv = os.path.join(protocoldir, 'split%d'%split, 'gallery_%d.csv'%split)
    print '\n'.join([probecsv, gallerycsv])

    ordered_probe_ids = []
    ordered_gallery_ids = []

    def getIdList(csvfile):
        ids = []
        with open(csvfile, 'r') as f:
            next(f) # skip header
            for l in f:
                tid = l.encode('utf-8').split(',')[0]
                if not any(ids) or tid != ids[-1]:
                    ids.append(tid)
        return ids

    ordered_probe_ids = getIdList(probecsv)
    ordered_gallery_ids = getIdList(gallerycsv)

    real_id_pairs = [[int(x[0]),int(x[1])] for x in product(ordered_probe_ids, ordered_gallery_ids)]
    test_id_pairs = zip(probe_ids, gallery_ids)

    sfy = []
    sfyhat = []
    sfpid = []
    sfgid = []

    quietprint('[janus.metrics.order_cs2_results]: Starting search...', 2)
    with Stopwatch() as sw:
        stuff = zip(y, yhat, test_id_pairs)
        stuff.sort(key=lambda p: p[2])
        for ids in real_id_pairs:
            ids = tuple(ids) # convert from list
            lb = lower_bound(stuff, ids, key=lambda x: x[2])
            assert lb >= 0, 'Key not found: [%d,%d]: \n%r\n%r'%(ids[0],ids[1], ids, stuff)
            assert ids[0]==stuff[lb][2][0], 'pid mismatch: %d, %d'%(ids[0],stuff[lb][2][0])
            assert ids[1]==stuff[lb][2][1], 'gid mismatch: %d, %d'%(ids[1],stuff[lb][2][1])
            sfy.append(stuff[lb][0])
            sfyhat.append(stuff[lb][1])
            sfpid.append(ids[0])
            sfgid.append(ids[1])
        assert len(sfy)==len(y), 'Failed to find all test pairs! len(y)==%d, len(sfy)==%d'%(len(y),len(sfy))
    quietprint('[janus.metrics.order_cs2_results]: Complete in %.1fs' % sw.elapsed, 2)
    return sfy, sfyhat, sfpid, sfgid







class CS3(object):
    def __init__(self, protocoldir, resultsdir=None):
        self.protocoldir = protocoldir
        self.resultsdir = resultsdir

    def __repr__(self):
        return str('<janus.metrics.cs3: protocoldir=%s>' % self.protocoldir)

    def _11_cov(self, verifycsv, refcsv, probecsv):

        h = readcsv(verifycsv, ' ')[0] # header only
        vcsv = readcsv(verifycsv, ' ')[1:] # header
        rcsv = readcsv(refcsv, ',')[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        rid_sid = { r[0]: r[1] for r in rcsv }  # reference template id to subject id
        pid_sid = { r[0]: r[1] for r in pcsv }  # probe template ud to subject id

        Y = [float(pid_sid[r[0]]==rid_sid[r[1]]) for r in vcsv]

        Y = np.array(Y, dtype=np.float32)
        k = h.index('SIMILARITY_SCORE')  # different
        Yhat = [float(r[k]) for r in vcsv]
        Yhat = np.array(Yhat, dtype=np.float32)

        return (Y, Yhat)


    def _11(self, verifycsv, probecsv, gals1csv, gals2csv):

        h = readcsv(verifycsv, ' ')[0] # header only
        if len(h) == 1:
            h = readcsv(verifycsv, ',')[0] # header only
            vcsv = readcsv(verifycsv, ',')[1:] # header
        else:
            h = readcsv(verifycsv, ' ')[0] # header only
            vcsv = readcsv(verifycsv, ' ')[1:] # header

        pcsv = readcsv(probecsv, ',')[1:] # header
        s1csv = readcsv(gals1csv, ',')[1:] # header
        s2csv = readcsv(gals2csv, ',')[1:] # header

        gcsv = s1csv + s2csv  # merge s1 and s2

        gid_sid = { r[0]: r[1] for r in gcsv }  # gallery template id to subject id
        pid_sid = { r[0]: r[1] for r in pcsv }  # probe template ud to subject id

        Y = [float(pid_sid[r[1]]==gid_sid[r[0]]) for r in vcsv]   # r[0] is gallery (reference), r[1] is probe (verify)

        Y = np.array(Y, dtype=np.float32)
        try:
            k = h.index('SIMILARITY_SCORE')  # older
        except:
            k = h.index('SCORE')  # newer

        Yhat = [float(r[k]) for r in vcsv]
        Yhat = np.array(Yhat, dtype=np.float32)

        return (Y, Yhat)


    def _1N(self, searchcsv, gallerycsv, probecsv):
        h = readcsv(searchcsv, ' ')[0] # header
        if len(h) == 1:
            h = readcsv(searchcsv, ',')[0] # header                    
            scsv = readcsv(searchcsv, ',')[1:] # header
        else:
            scsv = readcsv(searchcsv, ' ')[1:] # header
        gcsv = readcsv(gallerycsv, ',')[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        gid_to_subject = { r[0]: r[1] for r in gcsv }
        pid_to_subject = { r[0]: r[1] for r in pcsv }

        pid = list(OrderedDict.fromkeys([x[0] for x in pcsv]))  # unique template ids, order preserving
        gid = list(OrderedDict.fromkeys([x[0] for x in gcsv]))  # unique template ids, order preserving

        pid_to_index = { p : k for (k,p) in enumerate(pid) }
        gid_to_index = { g : k for (k,g) in enumerate(gid) }

        Y = [float(pid_to_subject[p] == gid_to_subject[g]) for (p,g) in product(pid, gid)]
        Y = np.array(Y, dtype=np.float32)
        Y.resize([len(pid), len(gid)])

        Yhat = -1E3*np.ones_like(Y)
        try:
            k_score = h.index('SIMILARITY_SCORE')  # OLDER
        except:
            k_score = h.index('SCORE')  # NEWER

        try:
            k_gid = h.index('GALLERY_TEMPLATE_ID')  # NEWER
        except:
            k_gid = 2  # OLDER

        for r in scsv:
            (i,j) = (pid_to_index[r[0]], gid_to_index[r[k_gid]])
            Yhat[i,j] = float(r[k_score])
            
        #n = len(set([int(r[1]) for r in scsv]))  # ranks

        #Y = [float(pid_sid[r[0]]==gid_sid[r[2]]) for r in scsv] # r[0] is probe, r[2] is gallery
        #Y = np.array(Y, dtype=np.float32)
        #Y.resize([len(Y)/n, n])

        #Yhat = [float(r[-1]) for r in scsv]
        #Yhat = np.array(Yhat, dtype=np.float32)
        #Yhat.resize([len(Yhat)/n, n])

        return (Y, Yhat)



    def cs3_1N_img_S1(self, searchcsv=None, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_img.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)


    def cs3_1N_img_S2(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_img.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)


    def cs3_1N_mixed_S1(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def cs3_1N_mixed_S2(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def cs3_1N_video_S1(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_video.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def cs3_1N_video_S2(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_video.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)


    def cs3_11_mixed(self, verifycsv, detFigure=2, prependToLegend='D3.0', hold=False):
        """input csv is verify.scores output"""
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_mixed.csv')
        s1csv = os.path.join(self.protocoldir, 'cs3_1N_gallery_S1.csv')
        s2csv = os.path.join(self.protocoldir, 'cs3_1N_gallery_S2.csv')
        (Y, Yhat) = self._11(verifycsv, probecsv, s1csv, s2csv)
        ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def cs3_11_cov(self, verifycsv, detFigure=2, prependToLegend='D3.0', hold=False):
        """input csv is verify.scores output"""

        probecsv = os.path.join(self.protocoldir, 'cs3_11_covariate_probe_metadata.csv')
        refcsv = os.path.join(self.protocoldir, 'cs3_11_covariate_reference_metadata.csv')
        (Y, Yhat) = self._11_cov(verifycsv, refcsv, probecsv)
        ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)


    def detection(self):
        detcsv = os.path.join(self.protocoldir, 'cs3_face_detection.csv')
        return readcsv(detcsv)


class CS4(CS3):

    def _11_cov(self, verifycsv, probecsv):

        csv = readcsv(verifycsv, ' ')
        h = csv[0] # header only
        vcsv = csv[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        pid_sid = { r[0]: r[1] for r in pcsv }  # probe template id to subject id

        Y = [float(pid_sid[r[0]]==pid_sid[r[1]]) for r in vcsv]

        Y = np.array(Y, dtype=np.float32)
        k = h.index('SIMILARITY_SCORE')  # different
        Yhat = [float(r[k]) for r in vcsv]
        Yhat = np.array(Yhat, dtype=np.float32)

        return (Y, Yhat)

    def _cs4_11_mixed(self, verifycsv):
        """input csv is verify.scores output"""
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        s1csv = os.path.join(self.protocoldir, 'cs4_1N_gallery_G1.csv')
        s2csv = os.path.join(self.protocoldir, 'cs4_1N_gallery_G2.csv')
        (Y, Yhat) = self._11(verifycsv, probecsv, s1csv, s2csv)
        return (Y,Yhat)

    def cs4_11_mixed(self, verifycsv, detFigure=2, prependToLegend='D4.0', hold=False):
        """input csv is verify.scores output"""
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        s1csv = os.path.join(self.protocoldir, 'cs4_1N_gallery_G1.csv')
        s2csv = os.path.join(self.protocoldir, 'cs4_1N_gallery_G2.csv')
        (Y, Yhat) = self._11(verifycsv, probecsv, s1csv, s2csv)
        return ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def cs4_11_cov(self, verifycsv, detFigure=2, prependToLegend='D4.0', hold=False):
        """input csv is verify.scores output"""

        probecsv = os.path.join(self.protocoldir, 'cs4_11_covariate_probe_reference.csv')
        (Y, Yhat) = self._11_cov(verifycsv, probecsv)
        return ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def _cs4_1N_mixed_G1(self, searchcsv):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return (Y, Yhat)
        
    def cs4_1N_mixed_G1(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)

    def _cs4_1N_mixed_G2(self, searchcsv):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return (Y, Yhat)

    def cs4_1N_mixed_G2(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)


    def cs4_1N_mixed_distractors(self, searchcsv, minDistractorId=1000000, split='G1', cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        if split == 'G1':
            gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G1.csv')
        else:
            gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G2.csv')

        with open(searchcsv, 'r') as f:
            list_of_rows_header = [x.strip() for x in f.readline().split(' ')]  # header
            list_of_rows = [[x.strip() for x in r.split(' ')] for r in f.readlines() if int(r.split(' ')[1]) < 50]  # only valid retrievals
        h = list_of_rows_header
        scsv = list_of_rows
        gcsv = readcsv(gallerycsv, ',')[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        gid_to_subject = { r[0]: r[1] for r in gcsv }
        pid_to_subject = { r[0]: r[1] for r in pcsv }

        pid = list(OrderedDict.fromkeys([x[0] for x in pcsv]))  # unique template ids, order preserving
        gid = list(OrderedDict.fromkeys([x[0] for x in gcsv]))  # unique template ids, order preserving
        did = list(set([r[2] for r in scsv if int(r[2]) >= minDistractorId]))  # unique distractor IDs for augmented gallery
        #gid = gid + did;  # append discractors to gallery

        pid_to_index = { p : k for (k,p) in enumerate(pid) }
        gid_to_index = { g : k for (k,g) in enumerate(gid) }
        z = gid_to_subject.copy();  z.update( {x:x for x in did} ); gid_to_subject = z.copy();  # distractor subject ID is template ID


        Y = [float(pid_to_subject[p] == gid_to_subject[g]) for (p,g) in product(pid, gid)]
        Y = np.array(Y, dtype=np.float32)
        Y.resize([len(pid), len(gid)])
        Y = np.hstack( (Y, np.zeros( (len(pid), 50) )) )

        Yhat = -1E3*np.ones_like(Y)
        k = h.index('SIMILARITY_SCORE')
        for r in scsv:
            if int(r[1]) < 50:
                if (int(r[2]) < minDistractorId):
                    (i,j) = (pid_to_index[r[0]], gid_to_index[r[2]])
                else:
                    (i,j) = (pid_to_index[r[0]], len(gid) + int(r[1]))
                Yhat[i,j] = float(r[k])

        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)
                    
