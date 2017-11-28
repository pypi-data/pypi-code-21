from __future__ import division, print_function
import numpy as np
import scipy.stats as st
import time
import multiprocessing
from EPIC import common, MCMC_chains, drawhistograms
import click
import os, sys

try:
    import cPickle as pickle
except ImportError:
    import pickle

def load_model_details(wdir):
    priors = pickle.load(open(os.path.join(wdir, 'priors.p'), 'rb'))
    nuisance = pickle.load(open(os.path.join(wdir, 'nuisance.p'), 'rb'))
    tex = pickle.load(open(os.path.join(wdir, 'tex.p'), 'rb'))
    parnames = pickle.load(open(os.path.join(wdir, 'parnames.p'), 'rb'))
    nparams = readint(os.path.join(wdir, 'nparams.txt'))
    nchains = readint(os.path.join(wdir, 'nchains.txt'))
    return priors, nuisance, tex, parnames, nparams, nchains    

def readchain_seq(wdir, i, stop_at=False, bar=None, L=None):
    l = np.loadtxt(os.path.join(wdir, 'PTchain%i.txt' % (i+1)), delimiter=',')

    gj = []
    for line in l:
        for _ in range(int(line[-1])):
            gj.append(line[:-1])
    gj = np.array(gj)

    if stop_at:
        gj = gj[:stop_at]
    
    if len(gj) % 2 == 1:
        gj = gj[:-1]

    if L:
        L[i] = gj

    if bar:
        bar.update(1)

    return gj

def find_max_logposterior(nparams, f, n, burnin):
    maxlog = np.nanmax(f[burnin:,nparams])
    max_index = list(f[:,nparams]).index(maxlog)
    bestfit = [f[max_index,i] for i in range(nparams)]
    return f[max_index, nparams], bestfit

def read_chains(wdir, nchains, calculate_evidence=False, stop_at=False, ssd=False, showbar=True, args=None):
    if args:
        # if a SSD is used it may be faster to read the chains in parallel. In this
        # case passing SSD in the arguments will use this option. In general, HD's
        # perform better reading the files sequentially. It is False by default.
        ssd = common.lookarg('SSD', args) or ssd
        calculate_evidence = common.lookarg('evidence', args) or calculate_evidence

    if not calculate_evidence:
        nchains = 1

    if ssd:
        manager = multiprocessing.Manager()
        print('Loading chains...')
        f = manager.list(range(nchains))
        jobs = [multiprocessing.Process(
            target=readchain_seq, 
            args=(wdir, i),
            kwargs={'stop_at': stop_at, 'L': f}
            ) for i in range(nchains)]

        for job in jobs:
            job.start()
        for job in jobs:
            job.join()

    else:
        loading_chains_label = common.fixed_length('Loading chains...')
        if showbar:
            with click.progressbar(length=nchains, width=10, show_pos=True, empty_char='.', label=loading_chains_label, info_sep='  |  ', show_eta=False) as bar:
                f = [readchain_seq(wdir, i, stop_at, bar) for i in range(nchains)]
        else:
            f = [readchain_seq(wdir, i, stop_at) for i in range(nchains)]

    return f

def load_chains(wdir, nparams, nnuis, nchains, priors, parnames, tex, bchain=1, calculate_evidence=False, stop_at=False, burnin=None, png=False, args=None):
    
    if args:
        # on which chain to base results (only first chain, bchain=1, makes sense, for beta = 0.
        # but it may be useful to look at others for debugging purposes
        bchain = common.lookarg1('bchain=', args, instance=int) or bchain

        png = common.lookarg('png', args) or png
        burnin = common.lookarg1('burnin=', args, instance=int) or burnin
        stop_at = common.lookarg1('stop_at=', args, instance=int) or stop_at
        plot_sequences = common.lookarg('plot_sequences', args)
        ACF = common.lookarg('ACF', args)
        calculate_evidence = common.lookarg('evidence', args) or calculate_evidence or bchain != 1 or plot_sequences or ACF

    f = read_chains(wdir, nchains, calculate_evidence=calculate_evidence, stop_at=stop_at, showbar=True, args=args)

    n, f = MCMC_chains.truncate(f, args=args)

    common.pasta(wdir, 'n%ib%i' % (n, bchain))

    burnin = burnin or n//2
    maxlogposterior, bestfit = find_max_logposterior(nparams, f[bchain-1], n, burnin)
    AIC, BIC = common.Information_Criteria(n, parnames, bestfit, priors, nparams, nnuis, maxlogposterior, wdir, b=bchain)
    print('BIC: %.3f' % BIC)
    print('AIC: %.3f' % AIC)

    if calculate_evidence:
        betas = np.loadtxt(os.path.join(wdir, 'betas.txt'))
        logevidence = logZ_thermo_integration(wdir, f, n, nparams, betas, burnin=burnin, png=png)
        print('logZ: %.3e' % logevidence)
        intp_logevidence = logZ_thermo_integration(wdir, f, n, nparams, betas, burnin=burnin, interpol=True, png=png)
        print('interpolated logZ: %.3e' % intp_logevidence)
        np.savetxt(os.path.join(wdir, 'logZ_n%i.txt' % n), [logevidence,])

    return bestfit, f, n

def logZ_thermo_integration(wdir, f, n, nparams, betas, burnin=None, interpol=False, png=False):
    from scipy import integrate
    burnin = burnin or n//2
    beta_means = np.array([f[m][burnin:,nparams+1].mean() for m, _ in enumerate(betas)])
    
    if interpol:
        from scipy import interpolate
        interp_beta_means = interpolate.interp1d(betas[::-1], beta_means[::-1], kind='linear')
        return integrate.quad(lambda b: interp_beta_means(b), betas[-1], 1)[0]
    else:
        np.savetxt(os.path.join(wdir, 'beta_means_n%i.txt' % n), list(zip(betas[::-1], beta_means[::-1])))
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(betas[::-1], beta_means[::-1], lw=1, marker='s', markersize=3)
        ax.set_xlabel(r'$\beta$')
        ax.set_xscale('log')
        ax.set_ylabel(r'$\left\langle \ln \left[ p\left(D \mid M, X, I\right) \right] \right\rangle_{\beta}$')
        fig.savefig(os.path.join(wdir, 'beta_means_n%i.pdf' % n))
        if png:
            fig.savefig(os.path.join(wdir, 'beta_means_n%i.png' % n))
        return integrate.simps(beta_means[::-1], x=betas[::-1])

def analyze_chains(wdir, combobins=[20], bchain=1, calculate_evidence=False, stop_at=False, wDE_list=None, use_derived = False, plot_sequences=False, ACF=False, THIN=1, usetex=False, burnin=None, png=False, SMOOTH=None, args=None):

    if args:
        # The number of bins for the histograms can be specified (default will be
        # 20). More than one value can be passed as a list of integers.
        combobins = common.lookarg1list('combobins=', args, instance=int) or combobins

        # Wether to compute or not wDE(a)
        wDE_list = common.lookarg1('wDE_of_a=', args) or wDE_list

        # Get distributions of derived parameters
        use_derived = common.lookarg('use_derived', args) or use_derived

        # wether to plot or not chain sequences for all parameters and autocorrelation
        plot_sequences = common.lookarg('plot_sequences', args) or plot_sequences
        ACF = common.lookarg('ACF', args) or ACF

        # thinning of autocorrelation plots
        THIN = common.lookarg1('thin=', args, instance=int) or THIN

        # wether to use tex in plots
        usetex = common.lookarg('usetex', args) or usetex

        # on which chain to base results (only first chain, bchain=1, makes sense, for beta = 0.
        # but it may be useful to look at others for debugging purposes
        bchain = common.lookarg1('bchain=', args, instance=int) or bchain

        # burnin can be different from n//2, since this is not using GelmanRubin
        burnin = common.lookarg1('burnin=', args, instance=int) or burnin
        stop_at = common.lookarg1('stop_at=', args, instance=int) or stop_at

        # calculate evidence
        calculate_evidence = common.lookarg('evidence', args) or calculate_evidence or bchain != 1 or plot_sequences or ACF

        png = common.lookarg('png', args) or png

        SMOOTH = common.lookarg1('smooth_hist=', args) or SMOOTH

    dirfiles = os.listdir(wdir)
    dirfiles = [df for df in dirfiles if not '.swp' in df]
    inifile = common.lookargext('.ini', dirfiles)
    binsfile = os.path.isfile(inifile.replace('.ini', '.bins')) and inifile.replace('.ini', '.bins')
    priors, nuisance, _, tex, parnames, nparams, nchains = common.load_chains_and_model_details(wdir)

    bf, f, n = load_chains(wdir, nparams, len(nuisance), nchains, priors, parnames, tex, burnin=burnin, stop_at=stop_at, bchain=bchain, calculate_evidence=False, args=args)    ## ^ also used by mc4
    burnin = burnin or n//2

    if plot_sequences:
        MCMC_chains.plot_seq(wdir, f, n, nchains, nparams, tex, parnames, thin=THIN, burnin=burnin, bchain=bchain, args=args)

    if ACF:
        twopar_conv_label = common.fixed_length('Calculating correlations...')
        with click.progressbar(length=nparams, width=10, show_pos=False, empty_char='.', label=twopar_conv_label, info_sep='  |  ', show_eta=False) as bar:
            jobs = [multiprocessing.Process(
                target=MCMC_chains.twopar_correlation, 
                args=(wdir, f, n, m, nparams, parnames),
                kwargs={'thin': THIN, 'burnin': burnin, 'args': args}
                ) for m in range(nchains-1)]
            jobs.append(multiprocessing.Process(
                target=MCMC_chains.twopar_correlation, 
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
                MCMC_chains.plot_correlations(wdir, n, m, nparams, parnames, tex, args=args)
                bar.update(1)

    if isinstance(combobins, int):
        combobins = [combobins]
    assert isinstance(combobins, list)
    listbinsdict = common.create_listbinsdict(os.path.join(wdir, 'n%ib%i' % (n, bchain)), combobins, binsfile, clear=False)

    # save bestfit
    np.savetxt(os.path.join(wdir, 'n%ib%i' % (n, bchain), 'bf.txt'), bf)

    ###------------------------------------------------------------------------
    chains = [f[bchain-1][burnin:,i] for i in range(nparams)]
    model = common.read_model_name(wdir, label='MODEL')
    der_parnames, der_chains, wDE_list = MCMC_chains.combine_chains_derived_parameters(
            [f[bchain-1],], n, parnames, model, wDE_list=wDE_list)
    if wDE_list is not None:
        np.savetxt(os.path.join(wdir, 'n%ib%i' % (n, bchain) , 'wDE_list.txt'), wDE_list)

    nderpars = use_derived and len(der_parnames)
    if nderpars:
        common.pasta(os.path.join(wdir, 'n%ib%i' % (n, bchain)), 'der_pars')
        pickle.dump(der_parnames, open(os.path.join(wdir, 'der_parnames.p'), 'wb'), 0)

    par_fits = [st.distributions.norm.fit(combo) for combo in chains]
    np.savetxt(os.path.join(wdir, 'n%ib%i' % (n, bchain), 'par_fits.txt'), par_fits)
    common.format_with_uncertainties(par_fits, os.path.join(wdir, 'n%ib%i' % (n, bchain)), 'format_par_fits.txt')
    if nderpars:
        der_par_fits = [st.distributions.norm.fit(chain) for chain in der_chains]
        common.format_with_uncertainties(der_par_fits, os.path.join(wdir, 'n%ib%i' % (n, bchain)), 'format_der_par_fits.txt')
        np.savetxt(os.path.join(wdir, 'n%ib%i' % (n, bchain), 'der_par_fits.txt'), der_par_fits)

    
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
            der_bf = MCMC_chains.der_bestfit(bf, parnames, model)
            np.savetxt(os.path.join(wdir, 'n%ib%i' % (n, bchain), 'der_pars', 'bf.txt'), der_bf)
            for binsdict in listbinsdict:
                common.pasta(os.path.join(wdir, 'n%ib%i' % (n, bchain), 'der_pars'), "results%i" % binsdict['default'])
            MCMC_chains.make_histograms(der_chains, os.path.join(wdir, 'n%ib%i' % (n, bchain), 'der_pars'), nderpars, der_parnames, None, tex, der_bf, listbinsdict, inifile, bar=bar, smooth=SMOOTH, thin=THIN)

        unconstrained = MCMC_chains.make_histograms(chains, os.path.join(wdir, 'n%ib%i' % (n, bchain)), nparams, parnames, priors, tex, bf, listbinsdict, inifile, bar=bar, smooth=SMOOTH, thin=THIN)

        MCMC_chains.make_2dhistograms(nparams, chains, parnames, priors, tex, os.path.join(wdir, 'n%ib%i' % (n, bchain)), listbinsdict, unconstrained, bar, smooth=SMOOTH, thin=THIN)

    return f, combobins, n, nparams, tex, parnames

def initialize(command_arguments):
    wdir = command_arguments[1]

    bchain = common.lookarg1('bchain=', command_arguments, instance=int) or 1

    print('Started on %s' % time.ctime())

    itime = time.time()

    f, combobins, n, nparams, tex, parnames = analyze_chains(wdir, bchain=bchain, args=command_arguments)

    calculate_R = common.lookarg1list('calculate_R=', command_arguments)
    if calculate_R:
        F = [f[bchain-1],]
        for extrachain in calculate_R:
            fnew = analyze_chains(extrachain, bchain=bchain, args=command_arguments)[0]
            F.append(fnew[bchain-1])
        n, F = MCMC_chains.truncate(F, args=command_arguments)
        _, hatRp = MCMC_chains.GelmanRubin(F, n, "n%ib%i" % (n, bchain), len(calculate_R)+1, nparams, wdir, lastfew=0, args=command_arguments)

        print('Convergence hatRp-1: \t ' + ', '.join(['%.4e' % (Rp-1) for Rp in hatRp]))

        with open(os.path.join(wdir, 'n%ib%i' % (n, bchain), 'convergence.txt'), 'a') as h:
            h.write('\n')
            h.write('Convergence hatRp-1: \t ' + ', '.join(["%.4e" % (Rp-1) for Rp in hatRp]) + '\n')

    print('n = %i' % n)
    ftime = time.time()
    print('Total time for data analysis: %s.' % common.printtime(ftime - itime))
    print('' )

    # Tells the program to plot or not the histograms in the end. If not
    # desired, include dontdraw in arguments
    plot_histograms = not common.lookarg('dontdraw', command_arguments)
    png = common.lookarg('png', command_arguments)
    UseTex = common.lookarg('usetex', command_arguments)

    if plot_histograms:

        nmodels = 3
        if calculate_R:
            import monitor
            plotting_individual_parameters = common.fixed_length('Plotting variances and ratio for each parameter...')
            with click.progressbar(length=nparams, show_pos=True, empty_char='.', width=10, label=plotting_individual_parameters, info_sep='  |  ', show_eta=False) as bar:
                monitor.monitor_each_parameter(os.path.join(wdir, "n%ib%i" % (n, bchain)), tex, parnames, nparams, bar=bar, UseTex=UseTex, png=png)

            plotting_mon = common.fixed_length('Plotting convergence monitoring parameters...')
            monitor.plot_monitor_convergence([os.path.join(wdir, "n%ib%i" % (n, bchain))], UseTex=UseTex, png=png)
        itime = time.time()
        for cb in combobins:
            drawhistograms.build_histograms([os.path.join(wdir, "n%ib%i" % (n, bchain), 'results%i' % cb)], args=command_arguments)
        ftime = time.time()
        print('Results plotted in %s.' % common.printtime(ftime - itime))
        print('')

if __name__ == '__main__':
    initialize(sys.argv)

