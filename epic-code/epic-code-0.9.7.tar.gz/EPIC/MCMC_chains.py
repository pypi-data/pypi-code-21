from __future__ import division
from __future__ import print_function 
import time
import numpy as np
import pdb
import os, sys
import itertools
import multiprocessing
import scipy.stats as st
from EPIC import common, drawhistograms
import click

try:
    import cPickle as pickle
except ImportError:
    import pickle

def plot_seq(wdir, seq, n, nchains, nparams, tex, parnames, thin=1, burnin=None, bchain=None, png=False, args=None):
    if args:
        png = common.lookarg('png', args) or png

    burnin = burnin or n//2

    plt = load_plt(args)
    fig, axes = plt.subplots(nparams, nchains, sharex='col')
    fig.set_size_inches(nchains*2.5, nparams*1.5)

    SeqLabel = common.fixed_length('Plotting sequences...')
    with click.progressbar(length=nparams*nchains, width=10, show_pos=False, empty_char='.', label=SeqLabel, info_sep='  |  ', show_eta=False) as bar:
        for i in range(nparams*nchains):
            jx, jy = divmod(i, nchains)
            axes[jx][jy].plot(range(seq[jy][:,jx].size)[burnin::thin], seq[jy][burnin::thin,jx], lw=0.5)
            bar.update(1)

    for j in range(nchains):
        axes[-1][j].set_xlabel('Sequence number')
        axes[0][j].xaxis.set_label_position('top')
        axes[0][j].set_xlabel('Chain %i' % (j+1))

    for i in range(nparams):
        axes[i][0].set_ylabel(r'$' + tex[parnames[i]] + '$')

    fig.tight_layout()
    #fig.subplots_adjust(hspace=0)
    if bchain is None:
        fig.savefig(os.path.join(wdir, 'n%i' % n, 'sequences.pdf'))
        if png:
            fig.savefig(os.path.join(wdir, 'n%i' % n, 'sequences.png'))
    else:
        fig.savefig(os.path.join(wdir, 'sequences%i.pdf' % n))
        if png:
            fig.savefig(os.path.join(wdir, 'sequences%i.png' % n))

def plot_correlations(wdir, n, m, nparams, parnames, tex, usetex=False, png=False, P0=None, args=None):
    
    if args:
        usetex = common.lookarg('usetex', args) or usetex
        png = common.lookarg('png', args) or png
        P0 = common.lookarg1('p0=', args, instance=int) or P0

    plt = load_plt(args)

    grid, subplots = plt.subplots(nparams, nparams, sharex='col', sharey='row')
    grid.set_size_inches(nparams*2.5, nparams*1.6)

    for i in range(nparams * nparams):
        jx, jy = divmod(i, nparams)
        if jx > jy:
            x, tpcorr = np.loadtxt(os.path.join(wdir, 'correlation_lengths_n%i' % n, 'corr%i_%s_%s.txt' % (m, parnames[jx], parnames[jy])), unpack=True)
            subplots[jx][jy].plot(x, tpcorr, lw=1, label=r'$' + tex[parnames[jy]] + r' \times ' + tex[parnames[jx]] + '$')
            subplots[jx][jy].axhline(0, ls='--', lw=0.3, color='k')
            #if P0:
            #    tau = common.fit_tau(x, tpcorr, P0)
            #    subplots[jx][jy].plot(common.exponential_corr(x, tau), lw=0.5, color='C1', ls=':', label=r'$\tau = ' + "%.2f" % tau + '$')
            #    np.savetxt(os.path.join(wdir, 'correlation_lengths_n%i' % n, 'tau%i_%s_%s.txt' % (m, parnames[jx], parnames[jy])), [tau,])
            subplots[jx][jy].legend(loc='upper right', frameon=False, borderaxespad=0.5, handletextpad=0.5)
            subplots[jx][jy].tick_params(size=3)
        elif jx < jy:
            grid.delaxes(subplots[jx][jy])

        else:
            x, aucorr = np.loadtxt(os.path.join(wdir, 'correlation_lengths_n%i' % n, 'aucorr%i_%s.txt' % (m, parnames[jx])), unpack=True)
            subplots[jx][jy].plot(x, aucorr, lw=1, label=r'$' + tex[parnames[jy]] + '$')
            subplots[jx][jy].axhline(0, ls='--', lw=0.3, color='k')
            if P0:
                tau = common.fit_tau(x, aucorr, P0)
                subplots[jx][jy].plot(common.exponential_corr(x, tau), lw=0.5, color='C1', ls=':', label=r'$\tau = ' + "%.2f" % tau + '$')
                np.savetxt(os.path.join(wdir, 'correlation_lengths_n%i' % n, 'tau%i_%s.txt' % (m, parnames[jx])), [tau,])
            subplots[jx][jy].legend(loc='upper right', frameon=False, borderaxespad=0.5, handletextpad=0.5)
            subplots[jx][jy].tick_params(size=3)

    for jy in range(nparams):
        subplots[-1][jy].set_xlabel('Lag')
        subplots[jy][0].set_ylabel('Correlation')

    grid.tight_layout()
    grid.subplots_adjust(hspace=0,wspace=0)
    grid.savefig(os.path.join(wdir, "correlation_lengths_n%i" % n, 'grid_chain%i.pdf' % (m+1)))
    if png:
        grid.savefig(os.path.join(wdir, "correlation_lengths_n%i" % n, 'grid_chain%i.png' % (m+1)))


def twopar_correlation(wdir, seq, n, m, nparams, parnames, thin=1, burnin=None, bar=None, args=None):
    if args:
        burnin = common.lookarg1('burnin=', args, instance=int) or burnin

    burnin = burnin or n//2

    if args:
        thin = common.lookarg1('thin=', args, instance=int) or thin

    chain_autocorr = []
    if nparams == 1:
        subplots = [[subplots,],]

    common.pasta(wdir, 'correlation_lengths_n%i' % n)

    for i in range(nparams * nparams):
        jx, jy = divmod(i, nparams)
        if jx > jy:
            lagsize = seq[m][burnin:,jx].size
            assert seq[m][burnin:,jy].size == lagsize
            tpcorr = [common.correlation(seq[m][burnin:,jy], seq[m][burnin:,jx], lag) for lag in range(lagsize//2)[::thin]]
            np.savetxt(os.path.join(wdir, 'correlation_lengths_n%i' % n, 'corr%i_%s_%s.txt' % (m, parnames[jx], parnames[jy])), list(zip(list(range(lagsize//2))[::thin], tpcorr))) 

        elif jx < jy:
            pass 

        else:
            lagsize = seq[m][burnin:,jx].size
            aucorr = [common.auto_correlation(seq[m][burnin:,jx], lag) for lag in range(lagsize//2)[::thin]]
            chain_autocorr.append(aucorr)
            np.savetxt(os.path.join(wdir, 'correlation_lengths_n%i'  % n, 'aucorr%i_%s.txt' % (m, parnames[jx])), list(zip(list(range(lagsize//2)[::thin]), aucorr)))
            if bar:
                bar.update(1)

    return chain_autocorr

def readchain_seq(wdir, i, bar=None, L=None):
    chain = np.loadtxt(os.path.join(wdir, 'reducedchain%i.txt' % (i+1)), delimiter=',')

    gj = []
    for line in chain[:,:]:
        for _ in range(int(line[-1])):
            gj.append(line[:-1])
    gj = np.array(gj)

    if L:
        L[i] = gj

    if bar:
        bar.update(1)

    return gj

def find_index_for_required_length(f, size):
    size= int(size)
    chains_index = []

    if size > 0:
        for ichain, a in enumerate(f):
            cburn = 0
            j = 0
            while cburn < size:
                try:
                    cburn += a[j,-1]
                except IndexError:
                    print(ichain)
                    raise IndexError
                j += 1
            else:
                j -= 1
                cburn -= a[j,-1]
            a[j,-1] -= (size-cburn)
            assert a[j,-1] >= 0
            chains_index.append(j)
            # reducedburn[j] are definitely different for each chain
    else:
        for ichain, a in enumerate(f):
            cburn = 0
            j = -1
            while cburn > size:
                try:
                    cburn -= a[j,-1]
                except IndexError:
                    print(ichain)
                    raise IndexError
                j -= 1
            else:
                j += 1
                cburn += a[j,-1]
            a[j,-1] -= (cburn-size)
            assert a[j,-1] >= 0
            chains_index.append(j)

    return chains_index, f

def truncate(f, stop_at=False, args=None):
    if args:
        # Alternatively to analysing the entire chains, the user can specify a maximum number of steps
        stop_at = common.lookarg1('stop_at=', args, instance=int) or stop_at

    f0 = [len(F) for F in f]

    small = min(f0)
    if stop_at:
        small = min(small, stop_at)
    if divmod(small, 2)[1] == 1:
        small -= 1

    newchains = [F[:small,:] for F in f]
    f0 = [len(F) for F in newchains]
    assert len(set(f0)) == 1
    n = f0[0]
    return n, newchains

def find_max_logposterior(nchains, nparams, f, n, h):
    maxlogposterior = []
    for j in range(nchains): # replace reducedburn[j]: with 1: to pick any bf among all points
        maxlog_thischain = np.nanmax(f[j][n//2:,nparams])  # here
        maxlogposterior.append(maxlog_thischain)
        max_index = list(f[j][:,nparams]).index(maxlog_thischain) # this is the index in the entire list, not the slice!!!
        out = '\t'.join(('(%.5f, %.5f, %.5f)' % (f[j][max_index,i], np.mean(f[j][n//2:,i]), np.sqrt(np.mean(abs(f[j][n//2:,i]-np.mean(f[j][n//2:,i]))**2))) for i in range(nparams)))
        h.write(out + '\n')
        #print(out)
    a_with_best_maxlog = maxlogposterior.index(max(maxlogposterior))
    max_index = list(f[a_with_best_maxlog][:,nparams]).index(np.nanmax(f[a_with_best_maxlog][n//2:,nparams])) # here, j = a_with_best_maxlog
    bestfit = [f[a_with_best_maxlog][max_index,i] for i in range(nparams)]
    return f[a_with_best_maxlog][max_index,nparams], bestfit

def estimate_sigma2(n, m, W, B_n):
    return (1-1/n) * W + (1 + 1/m) * B_n

def estimate_varV(n, m, B_n, s2, xbar, xbarbar):
    varV = (1-1/n)**2 / m * common.sample_variance(s2)
    varV += (1 + 1/m)**2 * 2 / (m - 1) * np.dot(B_n, B_n)
    last_term = 2 * (m+1) * (n-1) / m**2 / n # expression in the article: / m / n**2 * n/m
    last_term *= common.sample_covariance(s2, xbar**2) - 2 * xbarbar * common.sample_covariance(s2, xbar) # xbar**2 not matrix product
    varV += last_term
    return varV

def get_V_W_R(k, g, nchains, nparams, i_k=None, L=None, bar=None):
    psi_barj_bart = np.array([np.mean([np.mean(g[j][k//2:k,i]) for j in range(nchains)]) for i in range(nparams)])
    PW = np.zeros((nparams,nparams))
    PBn = np.zeros((nparams,nparams))
    pbn = 0
    s2, seq_means = [], []
    for j in range(nchains):
        s2.append(np.zeros(nparams))
        psij_bart = np.array([np.mean(g[j][k//2:k,i]) for i in range(nparams)])
        mb = psij_bart - psi_barj_bart
        pbn += mb**2 # not a matrix product
        mb = np.array(mb, ndmin=2)
        PBn += np.dot(mb.transpose(), mb)
        seq_means.append(psij_bart)
        for G in g[j][k//2:k,:]:
            m = np.array(G[:nparams]) - psij_bart
            M = np.array(m, ndmin=2)
            PW += np.dot(M.transpose(), M)
            s2[j] += m**2 # not a matrix product
        s2[j] /= k//2 - 1
        if bar:
            bar.update(1)

    w = np.array([np.mean([s2[j][i] for j in range(nchains)]) for i in range(nparams)])
    W = 1/(nchains*(k//2-1)) * PW
    Bovern = 1/(nchains-1) * PBn
    bovern = 1/(nchains-1) * pbn
    
    hatV = estimate_sigma2(k//2, nchains, W, Bovern)
    eigenvalues = np.linalg.eigvals(np.dot(np.linalg.inv(W), hatV))
    try:
        assert np.all(np.isreal(eigenvalues)) or np.all(np.abs(np.imag(eigenvalues)) < 1e-10)
    except AssertionError:
        print(eigenvalues)
        raise AssertionError
    eigenvalues = eigenvalues.real
    #print(eigenvalues)
    hatRp2 = max(eigenvalues)

    hatv = estimate_sigma2(k//2, nchains, w, bovern)
    hatrp2 = hatv/w

    varv = np.array([estimate_varV(k//2, nchains, bovern[i], np.array([S[i] for S in s2]), np.array([xmean[i] for xmean in seq_means]), psi_barj_bart[i]) for i in range(nparams)])
    df = 2 * np.dot(hatv, hatv) / varv
    hatrp2 *= (df+3)/(df+1)

    #res = np.array([k, np.sqrt(hatRp2), common.det(hatV), common.det(W)]), eigenvalues, hatV, W
    res = np.array([k, np.sqrt(hatRp2), common.det(hatV), common.det(W)]), np.array([np.sqrt(hatrp2), hatv, w])
    if L:
        L[i_k] = res

    return res

def GelmanRubin(f, n, nfolder, nchains, nparams, wdir, lastfew=0, step=20, args=None):
    if args:
        # this sets the number of intermediate steps when monitoring convergence,
        # for k between 0 and n.
        step = common.lookarg1('GRstep=', args, instance=int) or step
        step = max(2, step)

        lastfew = common.lookarg1('lastfew=', args, instance=int) or lastfew

    Monitoring_convergence_label = common.fixed_length('Monitoring convergence...')
    list_of_k = range(n, 1, -n//step)[::-1]
    if list_of_k[0] < (list_of_k[1] - list_of_k[0])//2:
        list_of_k = list_of_k[1:]
    list_of_k = list_of_k[lastfew:]

    manager = multiprocessing.Manager()
    if len(list_of_k) <= multiprocessing.cpu_count()-1:
        with click.progressbar(length=nchains, width=10, show_pos=False, empty_char='.', label=Monitoring_convergence_label, info_sep='  |  ', show_eta=False) as bar:
            monitor_convergence = manager.list(range(len(list_of_k)))
            jobs = [multiprocessing.Process(
                target=get_V_W_R, 
                args=(k, f, nchains, nparams),
                kwargs={'i_k': i_k, 'L': monitor_convergence}
                ) for i_k, k in enumerate(list_of_k[:-1])]
            # updates progressbar with the larger run only, since they will run at the same time
            jobs.append(multiprocessing.Process(
                target=get_V_W_R, 
                args=(list_of_k[-1], f, nchains, nparams),
                kwargs={'i_k': len(list_of_k)-1, 'L': monitor_convergence, 'bar': bar}
                ))
            for j in jobs:
                j.start()
            for j in jobs:
                j.join()

    else:
        with click.progressbar(length=len(list_of_k), width=10, show_pos=False, empty_char='.', label=Monitoring_convergence_label, info_sep='  |  ', show_eta=False) as bar:
            monitor_convergence = manager.list(range(len(list_of_k)))
            jobs = [multiprocessing.Process(
                target = get_V_W_R,
                args = (k, f, nchains, nparams),
                kwargs = {'i_k': i_k, 'L': monitor_convergence}
                ) for i_k, k in enumerate(list_of_k)]

            j = 0
            cpu = multiprocessing.cpu_count()
            for i in range(len(jobs)//cpu):
                for job in jobs[j:(i+1)*cpu]:
                    job.start()
                for job in jobs[j:(i+1)*cpu]:
                    job.join()
                    bar.update(1)
                j += cpu
            for job in jobs[j:(i+1)*cpu + len(jobs)%cpu]:
                job.start()
            for job in jobs[j:(i+1)*cpu + len(jobs)%cpu]:
                job.join()
                bar.update(1)

            #monitor_convergence = []
            #for k in list_of_k:
            #    monitor_convergence.append(get_V_W_R(k, f, nchains, nparams))
            #    bar.update(1)

    mv_stats, univ_stats = [], []
    for m_c in monitor_convergence:
        mv_stats.append(m_c[0])
        univ_stats.append(m_c[1])

    if nparams == 1:
        np.savetxt(os.path.join(wdir, nfolder, 'monitor_par0.txt'), [univ_stats[ik] for ik, _ in enumerate(list_of_k)])
    else:
        for i in range(nparams):
            np.savetxt(os.path.join(wdir, nfolder, 'monitor_par%i.txt' % i), [univ_stats[ik][:,i] for ik, _ in enumerate(list_of_k)])

    monitor_convergence = np.array(mv_stats)
    np.savetxt(os.path.join(wdir, nfolder, 'monitor_convergence.txt'), monitor_convergence)

    hatRp_of_k = monitor_convergence[:,1]

    return list_of_k, hatRp_of_k

def load_chains(workingdir, nparams, nnuis, nchains, priors, parnames, tex, stop_at=False, ssd=False, args=None):

    if args:
        # if a SSD is used it may be faster to read the chains in parallel. In
        # this case passing SSD in the arguments will use this option. In
        # general, HD's perform better reading the files sequentially. It is
        # False by default.
        ssd = common.lookarg('SSD', args) or ssd

        # Alternatively to analysing the entire chains, the user can specify a
        # maximum number of steps
        stop_at = common.lookarg1('stop_at=', args, instance=int) or stop_at

    if ssd:
        manager = multiprocessing.Manager()
        f = manager.list(range(nchains))
        jobs = [multiprocessing.Process(
            target=readchain_seq, 
            args=(workingdir, i),
            kwargs={'L': f}
            ) for i in range(nchains)]
        for job in jobs:
            job.start()
        for job in jobs:
            job.join()
    else:
        loading_chains_label = common.fixed_length('Loading chains...')
        with click.progressbar(length=nchains, width=10, show_pos=True, empty_char='.', label=loading_chains_label, info_sep='  |  ', show_eta=False) as bar:
            f = [readchain_seq(workingdir, i, bar) for i in range(nchains)]

    n, f = truncate(f, args=args)

    common.pasta(workingdir, 'n%i' % n)
    h = open(os.path.join(workingdir, "n%i" % n, 'convergence.txt'), 'w')
    h.write('\t\t\t\t\t\t\t'.join((parnames[i] for i in range(nparams))) + '\n')
    #print('\t\t\t\t'.join((parnames[i] for i in range(nparams))))
    out = '\t\t'.join(('(best-fit, mean, std)' for i in range(nparams)))
    h.write(out + '\n')
    #print(out)
    h.write('' + '\n')

    #print('')
    #chain_sizes = [int(f[j][reducedburn[j]:,-1].sum()) for j in range(nchains)]
    #assert len(set(chain_sizes)) == 1
    #n = chain_sizes[0] 

    maxlogposterior, bestfit = find_max_logposterior(nchains, nparams, f, n, h)
    AIC, BIC = common.Information_Criteria(n, parnames, bestfit, priors, nparams, nnuis, maxlogposterior, workingdir)
    if __name__ == '__main__':
        print('BIC: %.3f' % BIC)
        print('AIC: %.3f' % AIC)

    out = 'best-fit: ', dict(zip(parnames, bestfit))
    h.write(str(out) + '\n')
    h.write('\n')
    h.close()

    return bestfit, f, n

def make_histograms(combo, wdir, nparams, parnames, priors, tex, bestfit, listbinsdict, inifile, bar=None, smooth=None, kde_shuffle=False, thin=1, recalculate_kde=True, no_reflections=False): 

    # save histogram information of separated chains
    #for j, F in enumerate(f):
    #    print('Saved histogram for chain %i, parameters:' % j, end=' ')
    #    for i in range(nparams):
    #        HEIGHTS, BINS, WIDTHS = common.numpyhist(F[n//2:,i], 30)#, True, False, False, priors[parnames[i]].vmin, priors[parnames[i]].vmax) 
    #        for binsdict in listbinsdict:
    #            auxdirbins = "results%i" % binsdict['default']
    #            np.savetxt(os.path.join(wdir, auxdirbins, 'histHEIGHTS-%i-%s.txt' % (j, parnames[i])), HEIGHTS)
    #            np.savetxt(os.path.join(wdir, auxdirbins, 'histBINS-%i-%s.txt' % (j, parnames[i])), BINS)
    #            np.savetxt(os.path.join(wdir, auxdirbins, 'histWIDTHS-%i-%s.txt' % (j, parnames[i])), WIDTHS)
    #            print('%s' % parnames[i], end=' ')
    #    print('')
    array_split = {}
    for par in parnames:
        array_split[par] = None
    splitfile = os.path.isfile(inifile.replace('.ini', '.split' )) and inifile.replace('.ini', '.split')
    if splitfile:
        with open(splitfile, 'r') as sf:
            line = sf.readline()
            while line:
                line = line.strip().split()
                if len(line) > 1:
                    array_split[line[0]] = float(line[1])
                line = sf.readline()
         

    for binsdict in listbinsdict:
        auxdirbins = "results%i" % binsdict['default']
        weakly_constrained = {}
        for i in range(nparams):
            nbins = getbinsfromdict(parnames[i], binsdict)
            count, seps, widths = common.numpyhist(combo[i], nbins)#, True, False, False, priors[parnames[i]].vmin, priors[parnames[i]].vmax)
            weakly_constrained[parnames[i]] = False if no_reflections else (count.std()/count.mean() <= 0.5 or count.min() / count.max() >= 0.05 or count[0] / count.max() >= 0.05 or count[-1] / count.max() >= 0.05) 
            #weakly_constrained[parnames[i]] = True
            #print(np.sum(count * widths))
            #Ecount, Eseps, Ewidths = common.numpyhist(combo[i], nbins, normalize=False)#, True, False, False, priors[parnames[i]].vmin, priors[parnames[i]].vmax)
            #print(np.sum(Ecount * Ewidths))
            np.savetxt(os.path.join(wdir, auxdirbins, 'combocount-%s.txt' % parnames[i]), count)
            np.savetxt(os.path.join(wdir, auxdirbins, 'comboseps-%s.txt' % parnames[i]), seps)
            np.savetxt(os.path.join(wdir, auxdirbins, 'combowidths-%s.txt' % parnames[i]), widths)
            #print('Saved histogram for chains combined, parameter %s' % parnames[i])
            combo_totallength = len(combo[i])
            normalization = combo_totallength * (seps[-1]-seps[0])/len(count)
            count = np.array(count) * normalization

            np.savetxt(os.path.join(wdir, auxdirbins, 'doacount-%s.txt' % parnames[i]), count)
            np.savetxt(os.path.join(wdir, auxdirbins, 'seps-%s.txt' % parnames[i]), seps)
            np.savetxt(os.path.join(wdir, auxdirbins, 'normalization-%s.txt' % parnames[i]), (normalization,))
            #print('Saved marginalized histogram information for parameter %s' % parnames[i])
            
            bar.update(1)

        with open(os.path.join(wdir, auxdirbins, 'weakly_constrained.txt'), 'w') as wfile:
            for par in weakly_constrained.keys():
                wfile.write('\t'.join([par, str(weakly_constrained[par])]) + '\n')

        if smooth and smooth.lower() in ['kde', 'kdh', 'kde1']:
            #kde_time = time.time()
            jobs = []
            common.pasta(wdir, 'kde_estimates')
            for i, par in enumerate(parnames):
                density_file = os.path.join(wdir, 'kde_estimates', 'kde_density-%s.txt' % par)
                kded = os.path.isfile(density_file)
                if recalculate_kde or not kded: 
                    seps = np.loadtxt(os.path.join(wdir, auxdirbins, 'comboseps-%s.txt' % par))

                    try:
                        a_edg = priors[par].vmin
                        b_edg = priors[par].vmax
                    except (TypeError, KeyError):
                        a_edg = seps[0]
                        b_edg = seps[-1]

                    if weakly_constrained[par] and smooth and smooth.lower() in ['kdh',]:
                        count = np.loadtxt(os.path.join(wdir, auxdirbins, 'doacount-%s.txt' % par))
                        axpad = (seps[-1]-seps[0]) * 0.15
                        jobs.append(
                                multiprocessing.Process(
                                    target=common.make_kde,
                                    args=([seps[:-1]+np.diff(seps)/2,],),
                                    kwargs={
                                        'a_support': seps[0]-axpad, 
                                        'b_support': seps[-1]+axpad,
                                        'a_edg': a_edg, 'b_edg': b_edg, 
                                        'support_file': os.path.join(
                                            wdir, 'kde_estimates', 'kde_support-%s.txt' % par),
                                        'density_file': density_file, 'thin': 1, 
                                        'correct_boundaries': weakly_constrained[par], 
                                        'normalization': count,
                                        'kde_shuffle': kde_shuffle,
                                        'bar': bar
                                        }
                                    )
                                )
                    else:
                        axpad = (combo[i].max() - combo[i].min()) * 0.15
                        try:
                            hx1 = max(priors[par].vmin, combo[i].min()-axpad)
                            hx2 = min(priors[par].vmax, combo[i].max()+axpad)
                        except (TypeError, KeyError):
                            hx1 = seps[0] - axpad
                            hx2 = seps[-1] + axpad

                        if array_split[par] is not None:
                            jobs.append(
                                    multiprocessing.Process(
                                        target=common.make_kde,
                                        args=([
                                            combo[i][combo[i] < array_split[par]],
                                            combo[i][combo[i] > array_split[par]]
                                            ] if array_split[par] is not None else [combo[i],],),
                                        kwargs={
                                            'support_file': os.path.join(
                                                wdir, 'kde_estimates', 'kde_support-%s.txt' % par), 
                                            'density_file': density_file, 'thin': thin,
                                            'bar': bar
                                            }
                                        )
                                    )
                        else:
                            jobs.append(
                                    multiprocessing.Process(
                                        target=common.make_kde,
                                        args = ([combo[i],],),
                                        kwargs={
                                            'a_support': hx1, 'b_support': hx2, 
                                            'a_edg': a_edg, 'b_edg': b_edg,
                                            'support_file': os.path.join(
                                                wdir, 'kde_estimates', 'kde_support-%s.txt' % par), 
                                            'density_file': density_file, 'thin': thin,
                                            'correct_boundaries': weakly_constrained[par],
                                            'kde_shuffle': kde_shuffle,
                                            'bar': bar
                                            }
                                        )
                                    )
                else:
                    bar.update(1)


            for job in jobs:
                job.start()
            for job in jobs:
                job.join()

            #kde_time = time.time() - kde_time
            #print('kde estimation in %s' % common.printtime(kde_time))

    return weakly_constrained

def der_bestfit(bf, parnames, model):
    import derived_bf

    der_bf = derived_bf.build_derived_bestfit(bf, parnames, model)

    """
    bf_Os = [bf[parnames.index(par)] for par in ['Och2', 'Obh2', 'Orh2'] if par in parnames]
    bf_h2 = bf[parnames.index('h')]**2 
    der_bf = [bfO/bf_h2 for bfO in bf_Os]
    der_bf.append(1 - sum(bf_Os)/bf_h2)
    if 'Obh2' in parnames:
        der_bf = der_bf[:2] + [der_bf[0]+der_bf[1]] + der_bf[2:]
    if 'Deltaw' in parnames:
        der_bf.append(bf[parnames.index('w0')] + bf[parnames.index('Deltaw')])
        #der_bf.append(bf[parnames.index('wf')] + bf[parnames.index('Deltaw')])
    if 'w0' in parnames and 'wp' in parnames:
        tau = bf[parnames.index('tau')]
        at = bf[parnames.index('at')]
        w0 = bf[parnames.index('w0')]
        wp = bf[parnames.index('wp')]
        # model fv2
        #der_bf.append( (tau/(tau+1))**tau * at )  # astar
        #der_bf.append( wp + ( (w0-wp)*tau**tau * (tau+1)**(-tau-1) * at)/(1 - at**(-1/tau)) )  # wstar
        # model fv3
        der_bf.append( at/(2**tau) )  # astar
        der_bf.append( wp + 1/4 * (w0-wp) * at**(1/tau) / (1-at**(-1/tau)) )  # wstar
    if 'xi' in parnames:
        der_bf.append(-(1+3*bf[parnames.index('xi')])/(2+3*bf[parnames.index('xi')]))
    """

    """
        #with open('acceptable_NFW_fits.txt', 'r') as group_file:
        #with open('good_NFW_fits.txt', 'r') as group_file:
        with open('regular.txt', 'r') as group_file:
            clusters = group_file.readlines()
        clusters = [cl.strip() for cl in clusters]
        clusters = clusters[1:]
        for cl in clusters:        
            der_bf.append(0)
    """

    return der_bf
    
def analyze_chains(wdir, combobins=[20], wDE_list=None, use_derived=False, plot_sequences=False, ACF=False, THIN=1, burnin=None, png=False, SMOOTH=None, kde_shuffle=False, recalculate_kde=True, args=None):

    if args:
        # The number of bins for the histograms can be specified (default will be
        # 20). More than one value can be passed as a list of integers.
        combobins = common.lookarg1list('combobins=', args, instance=int) or combobins

        # Wether to compute or not wDE(a)
        wDE_list = common.lookarg1('wDE_of_a=', args) or wDE_list

        # Get distributions for derived parameters
        use_derived = common.lookarg('use_derived', args) or use_derived

        # wether to plot or not chain sequences for all parameters and autocorrelation
        plot_sequences = common.lookarg('plot_sequences', args) or plot_sequences
        ACF = common.lookarg('ACF', args) or ACF

        # thinning of autocorrelation plots
        THIN = common.lookarg1('thin=', args, instance=int) or THIN

        burnin = common.lookarg1('burnin=', args, instance=int) or burnin

        png = common.lookarg('png', args) or png

        SMOOTH = common.lookarg1('smooth_hist=', args) or SMOOTH

        kde_shuffle = common.lookarg('kde_shuffle', args) or kde_shuffle

        recalculate_kde = not common.lookarg('dont_recalculate_kde', args)

    dirfiles = os.listdir(wdir)
    dirfiles = [df for df in dirfiles if not '.swp' in df]
    inifile = common.lookargext('.ini', dirfiles)
    binsfile = os.path.isfile(inifile.replace('.ini', '.bins')) and inifile.replace('.ini', '.bins')
    priors, nuisance, _, tex, parnames, nparams, nchains = common.load_chains_and_model_details(wdir)

    bf, f, n = load_chains(wdir, nparams, len(nuisance), nchains, priors, parnames, tex, args=args)    ## ^ also used by mc4
    print("n = %i" % n)
    if plot_sequences:
        plot_seq(wdir, f, n, nchains, nparams, tex, parnames, thin=THIN, args=args)

    burnin = burnin or n//2 

    if ACF:
        twopar_conv_label = common.fixed_length('Calculating correlations...')
        with click.progressbar(length=nparams, width=10, show_pos=False, empty_char='.', label=twopar_conv_label, info_sep='  |  ', show_eta=False) as bar:
            jobs = [multiprocessing.Process(
                target=twopar_correlation, 
                args=(wdir, f, n, m, nparams, parnames),
                kwargs={'thin': THIN, 'burnin': burnin, 'args': args}
                ) for m in range(nchains-1)]
            jobs.append(multiprocessing.Process(
                target=twopar_correlation, 
                args=(wdir, f, n, nchains-1, nparams, parnames),
                kwargs={'thin': THIN, 'burnin': burnin, 'bar': bar, 'args': args}
                ))
            for j in jobs:
                j.start()
            for j in jobs:
                j.join()

        twopar_saving_label = common.fixed_length('Plotting correlations...')
        with click.progressbar(length=nchains, width=10, show_pos=False, empty_char='.', label=twopar_saving_label, info_sep='  |  ', show_eta=False) as bar:
            for m in range(nchains):
                plot_correlations(wdir, n, m, nparams, parnames, tex, args=args)
                bar.update(1)

    if isinstance(combobins, int):
        combobins = [combobins]
    assert isinstance(combobins, list)
    listbinsdict = common.create_listbinsdict(os.path.join(wdir, 'n%i' % n), combobins, binsfile, clear=True)

    # save bestfit
    np.savetxt(os.path.join(wdir, 'n%i' % n, 'bf.txt'), bf)

    ###------------------------------------------------------------------------
    #print('best-fit: ', dict(zip(parnames, bf))     ## v used by analisaconvergencia only)
    combo_chains = combine_chains_for_each_parameter(f, burnin, nchains, nparams)
    model = common.read_model_name(wdir, label='MODEL')
    der_parnames, der_combo_chains, wDE_list = combine_chains_derived_parameters(
            f, n, parnames, model, wDE_list=wDE_list, THIN=THIN, args=args)
    if wDE_list is not None:
        with open(os.path.join(wdir, 'n%i' % n, 'wDE_list.txt'), 'w') as wDEfile:
            for wline in wDE_list:
                wDEfile.write('\t'.join(["%.5f" % w_el for w_el in wline]) + '\n')

    nderpars = use_derived and len(der_parnames)
    if nderpars:
        common.pasta(os.path.join(wdir, 'n%i' % n), 'der_pars')
        pickle.dump(der_parnames, open(os.path.join(wdir, 'der_parnames.p'), 'wb'), 0)
            
    #combo_res = dict(zip(parnames, [(np.average(A[:,0], weights=A[:,1]), np.sqrt(np.average(abs(A[:,0]-np.average(A[:,0], weights=A[:,1]))**2, weights=A[:,1]))) for A in combo_chains]))
    #out = 'Combined chains distribution: ' + str(combo_res)
    #print('' )
    #print(out    )

    par_fits = [st.distributions.norm.fit(combo) for combo in combo_chains]
    np.savetxt(os.path.join(wdir, 'n%i' % n, 'par_fits.txt'), par_fits)
    common.format_with_uncertainties(par_fits, os.path.join(wdir, 'n%i' % n), 'format_par_fits.txt')
    if nderpars:
        der_par_fits = [st.distributions.norm.fit(combo) for combo in der_combo_chains]
        common.format_with_uncertainties(der_par_fits, os.path.join(wdir, 'n%i' % n), 'format_der_par_fits.txt')
        np.savetxt(os.path.join(wdir, 'n%i' % n, 'der_par_fits.txt'), der_par_fits)

    sigf = np.array([fit[1] for fit in par_fits])
    sigd = 2.38 * sigf / np.sqrt(nparams)

    list_of_files = os.listdir(wdir)
    list_of_files = [filename for filename in list_of_files if not '.un~' in filename]
    list_of_files = [filename for filename in list_of_files if not '.swp' in filename]
    sourceinifile = common.lookargext('.ini', list_of_files)[:-4]
    with open(os.path.join(wdir, 'n%i' % n, "%s.mqparfits" % sourceinifile), 'w') as mqpf:
        for par, sig in zip(parnames, sigd):
            mqpf.write('\t'.join([par, str( sig/priors[par].interval_size )]) + '\n')
        #for par, csize, fits in zip(parnames, sizes, par_fits):
        #    mqpf.write('\t'.join([par, str(fits[1] / np.sqrt(csize) / priors[par].interval_size)]) + '\n')


    numberhists = nparams + (nparams*(nparams-1))//2 + nderpars # which can be zero
    
    saving_histograms_label = 'Saving information for histograms'
    if SMOOTH and SMOOTH.lower() in ['kde', 'kde1', 'kde2']:
        saving_histograms_label += ' and KDE estimates'
        if SMOOTH.lower() in ['kde', 'kde1']:
            numberhists += nderpars + nparams
        if SMOOTH.lower() in ['kde', 'kde2']:
            numberhists += (nparams*(nparams-1))//2
    numberhists *= len(listbinsdict)

    saving_histograms_label += '...'
    saving_histograms_label = common.fixed_length(saving_histograms_label)
    with click.progressbar(length=numberhists, width=10, show_pos=False, empty_char='.', label=saving_histograms_label, info_sep='  |  ', show_eta=False) as bar:

        #derived_parameters
        if nderpars:
            der_bf = der_bestfit(bf, parnames, model)
            np.savetxt(os.path.join(wdir, 'n%i' % n, 'der_pars', 'bf.txt'), der_bf)
            for binsdict in listbinsdict:
                common.pasta(os.path.join(wdir, 'n%i' % n, 'der_pars'), "results%i" % binsdict['default'], clear=True)
            make_histograms(der_combo_chains, os.path.join(wdir, 'n%i' % n, 'der_pars'), nderpars, der_parnames, None, tex, der_bf, listbinsdict, inifile, bar=bar, smooth=SMOOTH, kde_shuffle=kde_shuffle, thin=THIN, recalculate_kde=recalculate_kde, no_reflections=True)

        unconstrained = make_histograms(combo_chains, os.path.join(wdir, 'n%i' % n), nparams, parnames, priors, tex, bf, listbinsdict, inifile, bar=bar, smooth=SMOOTH, kde_shuffle=kde_shuffle, thin=THIN, recalculate_kde=recalculate_kde)

        make_2dhistograms(nparams, combo_chains, parnames, priors, tex, os.path.join(wdir, 'n%i' % n), listbinsdict, unconstrained, bar, smooth=SMOOTH, thin=THIN, recalculate_kde=recalculate_kde)

    return f, combobins, n, nparams, nchains, tex, parnames

def combine_chains_for_each_parameter(f, burnin, nchains, nparams):
    ff = [np.concatenate([F[burnin:,i] for F in f]) for i in range(nparams)]
    return ff

def combine_chains_derived_parameters(f, n, parnames, model, burnin=None, wDE_list=None, THIN=1, kde_shuffle=False, args=None):

    if args:
        THIN = common.lookarg1('thin=', args, instance=int) or THIN
        kde_shuffle = common.lookarg('kde_shuffle', args) or kde_shuffle

    burnin = burnin or n//2

    if wDE_list:
        #### Estimating wDE(a)
        from hobservables import wDE1 as wDE
        WP = np.concatenate([F[burnin:,parnames.index('wp')] for F in f])
        WF = np.concatenate([F[burnin:,parnames.index('wf')] for F in f])
        AT = np.concatenate([F[burnin:,parnames.index('at')] for F in f])
        TAU = np.concatenate([F[burnin:,parnames.index('tau')] for F in f])
        A = np.linspace(np.log(1e-2), np.log(1e1), 200)
        A = np.exp(A)
        wDE_list = []
        saving_wDElist_label = common.fixed_length('Saving wDE_list...')
        with click.progressbar(length=A.size, width=10, show_pos=False, empty_char='.', label=saving_wDElist_label, info_sep='  |  ', show_eta=False) as bar:
            for a in A:
                wDE_a = wDE(a, {'wp': WP, 'wf': WF, 'at': AT, 'tau': TAU}, {})
                assert wDE_a.size == AT.size
                if wDE_list and wDE_list.lower() in ['kde', 'kde1']:
                    wa = wDE_a.min()
                    wb = wDE_b.max()
                    wDE_support, wDE_density = common.make_kde([wDE_a,], a=wa, b=wb, thin=THIN, correct_boundaries=True, kde_shuffle=kde_shuffle)
                    wDE_1sigma, wDE_density = common.sigmalevels_1D(wDE_density, wDE_support, levels=[1,])
                    wDE_peaks1s = np.where(wDE_density > wDE_1sigma)[0]
                    wDE_sep_peaks = common.listsplit(wDE_peaks1s)
                    wDE_LIM1s  = [(wDE_support[peaks[0]], wDE_support[peaks[-1]]) for peaks in wDE_sep_peaks] 
                    wDE_LIM1s = wDE_LIM1s.flatten()
                    wDE_list.append(np.concatenate([np.array([a]), wDE_LIM1s]))
                else:
                    wDEmu, wDEsig = st.distributions.norm.fit(wDE_a)
                    wDE_list.append([a, wDEmu-wDEsig, wDEmu+wDEsig])
                bar.update(1)

    import derived
    der_parnames, der_combo_chains = derived.build_derived_parameters(f, burnin, parnames, model)

    #if 'xi' in parnames:
    #    TVR = np.concatenate([-(1+3*F[burnin:,parnames.index('xi')])/(2+3*F[burnin:,parnames.index('xi')]) for F in f])
    #    der_combo_chains.append(TVR)
    #    der_parnames.append('TVR')

    """
        from hobservables import a
        from load_data import Cluster
        with open('regular.txt', 'r') as group_file:
        #with open('good_NFW_fits.txt', 'r') as group_file:
        #with open('acceptable_NFW_fits.txt', 'r') as group_file:
            clusters = group_file.readlines()
        clusters = [cl.strip() for cl in clusters]
        obsble = clusters[0]
        clusters = clusters[1:]
        for cl in clusters:
            cluster = Cluster(cl, obsble)
            np.random.shuffle(cluster.r200)
            np.random.shuffle(cluster.M200)
            np.random.shuffle(cluster.c)
            np.random.shuffle(cluster.kTX)
            np.random.shuffle(cluster.fc)
            np.random.shuffle(cluster.dFdc)
            h = np.concatenate([F[burnin:,parnames.index('h')] for F in f])
            Och2 = np.concatenate([F[burnin:,parnames.index('Och2')] for F in f])
            xi = np.concatenate([F[burnin:,parnames.index('xi')] for F in f])
            g = np.concatenate([F[burnin:,parnames.index('gamma')] for F in f])
            cluster.r200 = cluster.r200[:h.size]
            cluster.M200 = cluster.M200[:h.size]
            cluster.c = cluster.c[:h.size]
            cluster.kTX = cluster.kTX[:h.size]
            cluster.fc = cluster.fc[:h.size]
            cluster.dFdc = cluster.dFdc[:h.size]
            a_of_z = a(cluster.z)
            E2h2 = h**2 + Och2*(a_of_z**(-3*(1-xi)) - 1)/(1-xi)
            Hz = 100 * np.sqrt(E2h2)/ h
            rhoc = common.rho_critical(Hz)
            Gprime_over_F = cluster.fc / cluster.r200**2
            Gprime_over_F *= 1 / rhoc * (- 9)/(8*np.pi) /200 / common.GmumH # 1/keV
            dlnF_times_r200 = 2 - cluster.dFdc/cluster.fc * cluster.c # this product is adimensional
            dlnrhoH = (3 * Gprime_over_F * cluster.kTX + dlnF_times_r200)
            dlnrhoH *= (g**2 * 3**(g+1))**(1/(1-g))
            dlnrhoH /= Hz
            DfE = (- 1/(2+3*xi)) * dlnrhoH /TVR
            DfE = DfE[DfE > -0.07]
            DfE = DfE[DfE < 0.07]
            print(DfE.size)
            der_combo_chains.append(DfE)
            der_parnames.append('DfE_EVR_%s' % cl)
    """

    return der_parnames, der_combo_chains, wDE_list

def getbinsfromdict(par, binsdict):
    try:
        return binsdict[par]
    except KeyError:
        return binsdict['default']

def make_2dhistograms(nparams, combo, parnames, priors, tex, wdir, listbinsdict, weakly_constrained, bar, smooth=None, thin=1, recalculate_kde=True):

    for binsdict in listbinsdict:
        auxdirbins = "results%i" % binsdict['default']
        #collectH = []
        for i in range(nparams*nparams):
            jx, jy = divmod(i, nparams)
            if jx > jy:
                ax = np.array(combo[jy])
                ay = np.array(combo[jx])
                np.savetxt(os.path.join(wdir, auxdirbins, 'corr_xy-%s-%s.txt' % (parnames[jx], parnames[jy])), (common.correlation(ax, ay, 0),))
                ws = None # np.array([c[1] for c in combo[jx]])

                #hrange = [[priors[parnames[jy]].vmin, priors[parnames[jy]].vmax], [priors[parnames[jx]].vmin, priors[parnames[jx]].vmax]]
                axpad = (ax.max() - ax.min()) * 0.15
                hx1 = max(ax.min()-axpad, priors[parnames[jy]].vmin)
                hx2 = min(ax.max()+axpad, priors[parnames[jy]].vmax)
                aypad = (ay.max() - ay.min()) * 0.15
                hy1 = max(ay.min()-aypad, priors[parnames[jx]].vmin)
                hy2 = min(ay.max()+aypad, priors[parnames[jx]].vmax)
                hrange = [[hx1, hx2], [hy1, hy2]]
                jxbins = getbinsfromdict(parnames[jx], binsdict)
                jybins = getbinsfromdict(parnames[jy], binsdict)
                ##rmsbins = np.sqrt(np.mean(np.square([jxbins, jybins])))
                ##rmsbins = np.sqrt(rmsbins*rmsbins/2)
                ##rmsbins = int(round(rmsbins))
                ##H, xedg, yedg = np.histogram2d(ax, ay, bins=rmsbins, range=hrange, normed=False, weights=ws)
                H, xedg, yedg = np.histogram2d(ax, ay, bins=[jxbins, jybins], range=hrange, normed=False, weights=ws)
                np.savetxt(os.path.join(wdir, auxdirbins, 'xedg-%s-%s.txt' % (parnames[jx], parnames[jy])), xedg)
                np.savetxt(os.path.join(wdir, auxdirbins, 'yedg-%s-%s.txt' % (parnames[jx], parnames[jy])), yedg)
                #collectH.append(H)
                np.savetxt(os.path.join(wdir, auxdirbins, 'H-%s-%s.txt' % (parnames[jx], parnames[jy])), H)
                np.savetxt(os.path.join(wdir, auxdirbins, 'hrange-%s-%s.txt' % (parnames[jx], parnames[jy])), hrange)

                XX, YY = np.meshgrid(xedg, yedg)
                np.savetxt(os.path.join(wdir, auxdirbins, 'XX-%s-%s.txt' % (parnames[jx], parnames[jy])), XX)
                np.savetxt(os.path.join(wdir, auxdirbins, 'YY-%s-%s.txt' % (parnames[jx], parnames[jy])), YY)
                bar.update(1)

            elif jx < jy:
                pass
            else:
                pass

        if smooth and smooth.lower() in ['kde', 'kdh', 'kde2']:
            #kde_time = time.time()
            jobs = []
            #print('Calculating 2D kernel density estimates...')
            common.pasta(wdir, 'kde_estimates')
            for i in range(nparams*nparams):
                jx, jy = divmod(i, nparams)
                if jx > jy:
                    density_file = os.path.join(wdir, 'kde_estimates', 'kde2d_density-%s-%s.txt' % (parnames[jx], parnames[jy]))
                    kded = os.path.isfile(density_file)
                    if recalculate_kde or not kded:
                        ax = np.array(combo[jy])
                        ay = np.array(combo[jx])
                        if weakly_constrained[parnames[jx]]:
                            hy1 = priors[parnames[jx]].vmin 
                            hy2 = priors[parnames[jx]].vmax 
                        else:
                            aypad = (ay.max() - ay.min()) * 0.15
                            hy1 = max(ay.min()-aypad, priors[parnames[jx]].vmin)
                            hy2 = min(ay.max()+aypad, priors[parnames[jx]].vmax)

                        if weakly_constrained[parnames[jy]]:
                            hx1 = priors[parnames[jy]].vmin
                            hx2 = priors[parnames[jy]].vmax
                        else:
                            axpad = (ax.max() - ax.min()) * 0.15
                            hx1 = max(ax.min()-axpad, priors[parnames[jy]].vmin)
                            hx2 = min(ax.max()+axpad, priors[parnames[jy]].vmax)

                        kde_hrange = [[hx1, hx2], [hy1, hy2]]
                        np.savetxt(os.path.join(wdir, 'kde_estimates', 'kde2d_hrange-%s-%s.txt' % (parnames[jx], parnames[jy])), kde_hrange)
                        xedg = np.loadtxt(os.path.join(wdir, auxdirbins, 'xedg-%s-%s.txt' % (parnames[jx], parnames[jy])))
                        yedg = np.loadtxt(os.path.join(wdir, auxdirbins, 'yedg-%s-%s.txt' % (parnames[jx], parnames[jy])))

                        xa_edg = priors[parnames[jy]].vmin # xedg[0]
                        xb_edg = priors[parnames[jy]].vmax # xedg[-1]
                        ya_edg = priors[parnames[jx]].vmin # yedg[0]
                        yb_edg = priors[parnames[jx]].vmax # yedg[-1]

                        if (weakly_constrained[parnames[jx]] or weakly_constrained[parnames[jy]]) and smooth and smooth.lower() in ['kdh',]:
                            H = np.loadtxt(os.path.join(wdir, auxdirbins, 'H-%s-%s.txt' % (parnames[jx], parnames[jy])))
                            AX = xedg[:-1] + np.diff(xedg)/2
                            AY = yedg[:-1] + np.diff(yedg)/2
                            AX, AY = np.array([[(x, y) for y in AY] for x in AX]).reshape(AX.size*AY.size, 2).transpose()
                            bandwidth = np.cov(ax, ay)
                            corr = bandwidth[0,1]/ax.std()/ay.std()
                            _, xstd = common.general_average_std(AX, weights=H.transpose().flatten())
                            _, ystd = common.general_average_std(AY, weights=H.transpose().flatten())
                            corrxy = corr * xstd * ystd
                            bandwidth = np.array([[xstd*xstd, corrxy], [corrxy, ystd*ystd]])
                            jobs.append(
                                    multiprocessing.Process(
                                        target=common.make_kde2d,
                                        args=([AX,], [AY,]),
                                        kwargs={
                                            'xa_support': hx1, 'xb_support': hx2,
                                            'ya_support': hy1, 'yb_support': hy2,
                                            'xa_edg': xa_edg, 'xb_edg': xb_edg, 
                                            'ya_edg': ya_edg, 'yb_edg': yb_edg,
                                            'bandwidth': bandwidth,
                                            'xsupport_file': os.path.join(wdir,
                                                'kde_estimates',
                                                'kde2d_xsupport-%s-%s.txt' %\
                                                        (parnames[jx], parnames[jy])),
                                            'ysupport_file': os.path.join(wdir,
                                                'kde_estimates',
                                                'kde2d_ysupport-%s-%s.txt' %\
                                                        (parnames[jx], parnames[jy])),
                                            'density_file': density_file, 'thin': 1, 
                                            'correct_boundaries': weakly_constrained[parnames[jx]] \
                                                    or weakly_constrained[parnames[jy]],
                                            'normalization': H.flatten(),
                                            'bar': bar
                                            }
                                        )
                                    )

                        else:
                            jobs.append(
                                    multiprocessing.Process(
                                        target=common.make_kde2d,
                                        args=([ax,], [ay,]),
                                        kwargs={
                                            'xa_support': hx1, 'xb_support': hx2, 
                                            'ya_support': hy1, 'yb_support': hy2,
                                            'xa_edg': xa_edg, 'xb_edg': xb_edg,
                                            'ya_edg': ya_edg, 'yb_edg': yb_edg,
                                            'xsupport_file': os.path.join(wdir,
                                                'kde_estimates',
                                                'kde2d_xsupport-%s-%s.txt' %\
                                                        (parnames[jx], parnames[jy])),
                                            'ysupport_file': os.path.join(wdir,
                                                'kde_estimates',
                                                'kde2d_ysupport-%s-%s.txt' %\
                                                        (parnames[jx], parnames[jy])),
                                            'density_file': density_file, 'thin': thin,
                                            'correct_boundaries': weakly_constrained[parnames[jx]] \
                                                    or weakly_constrained[parnames[jy]],
                                            'bar': bar
                                            }
                                        )
                                    )
                    else:
                        bar.update(1)

                else:
                    pass

            # may need a smaller number if the chains are too big
            #cpu = min(4, multiprocessing.cpu_count())
            cpu = multiprocessing.cpu_count()

            if cpu < len(jobs):
                j = 0
                for i in range(len(jobs)//cpu):
                    for job in jobs[j:(i+1)*cpu]:
                        job.start()
                    for job in jobs[j:(i+1)*cpu]:
                        job.join()
                    j += cpu
                for job in jobs[j:(i+1)*cpu + len(jobs)%cpu]:
                    job.start()
                for job in jobs[j:(i+1)*cpu + len(jobs)%cpu]:
                    job.join()
                    bar.update(1)
            else:
                for job in jobs:
                    job.start()
                for job in jobs:
                    job.join()

            #kde_time = time.time() - kde_time
            #print('kde 2d estimation in %s' % common.printtime(kde_time))

        
def load_plt(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt


    # wether to use tex in plots
    if args:
        UseTex = common.lookarg('usetex', args)
    else:
        UseTex = False

    if UseTex:
        plt.rc('font',**{'family':'serif','serif':['cmr10']}) # 'Times'
        plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}', r'\usepackage{siunitx}']
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

    return plt

def initialize(command_arguments):

    png = common.lookarg('png', command_arguments)
    UseTex = common.lookarg('usetex', command_arguments)
    workingdir = command_arguments[1]

    print('Started on %s' % time.ctime())

    itime = time.time()

    f, combobins, n, nparams, nchains, tex, parnames = analyze_chains(workingdir, args=command_arguments) # lastfew=0

    calculate_R = common.lookarg('calculate_R', command_arguments)
    if calculate_R:
        _, hatRp = GelmanRubin(f, n, "n%i" % n, nchains, nparams, workingdir, lastfew=0, args=command_arguments)

        print('Convergence hatRp-1: \t ' + ', '.join(['%.4e' % (Rp-1) for Rp in hatRp]))

        with open(os.path.join(workingdir, 'n%i' % n, 'convergence.txt'), 'a') as h:
            h.write('\n')
            h.write('Convergence hatRp-1: \t ' + ', '.join(["%.4e" % (Rp-1) for Rp in hatRp]) + '\n')

    #print('n = %i' % n)
    ftime = time.time()
    print('Total time for data analysis: %s.' % common.printtime(ftime - itime))
    print('')

    # Tells the program to plot or not the histograms in the end. If not
    # desired, include dontdraw in arguments
    plot_histograms = not common.lookarg('dontdraw', command_arguments)

    if plot_histograms:

        if calculate_R:
            import monitor
            plotting_individual_parameters = common.fixed_length('Plotting variances and ratio for each parameter...')
            with click.progressbar(length=nparams, show_pos=True, empty_char='.', width=10, label=plotting_individual_parameters, info_sep='  |  ', show_eta=False) as bar:
                monitor.monitor_each_parameter(os.path.join(workingdir, "n%i" % n), tex, parnames, nparams, bar=bar, UseTex=UseTex, png=png)

            plotting_mon = common.fixed_length('Plotting convergence monitoring parameters...')
            monitor.plot_monitor_convergence([os.path.join(workingdir, "n%i" % n)], UseTex=UseTex, png=png)

        itime = time.time()
        for cb in combobins:
            drawhistograms.build_histograms([os.path.join(workingdir, "n%i" % n, 'results%i' % cb)], args=command_arguments)
        ftime = time.time()
        print('Results plotted in %s.' % common.printtime(ftime - itime))
        print('')

if __name__ == '__main__':
    #multiprocessing.freeze_support()
    initialize(sys.argv)

