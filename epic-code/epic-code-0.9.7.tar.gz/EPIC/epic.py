from __future__ import division, print_function
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import collections
#import scipy.stats as st
#import ipdb as pdb
import numpy as np
import shutil
import sys, os
import itertools
from time import time, ctime, sleep
import multiprocessing
#import zipfile
from EPIC import initialize_chains
from EPIC import common, load_data, likelihood
from EPIC.hobservables import H
from EPIC import MCMC_chains, drawhistograms, remove_bad_chains
import ctypes

try:
    import cPickle as pickle
except ImportError:
    import pickle

#Msun = 1.98855e30 # in units of kg
#mumH = 0.63 * 1.67262178e-27 # in units of kg 
#mumH *= kg # in keV (km/s)**-2
#G_times_mumH = G * mumH

def load_ini(wdir, inifile):
    print('')
    print('Loading INI file...' )
    lines = common.readfile(os.path.join(wdir, inifile))

    model = common.read1linestring(lines, 'MODEL')
    obsbles = common.looktagstrings(lines, 'DATA')
    nBIC, labels, datapoints = load_data.load_data(obsbles)

    common.saveint(os.path.join(wdir, 'nBIC.txt'), nBIC)

    lf = open(os.path.join(wdir, 'labels.txt'), 'w')
    for lbl in labels:
        lf.write(lbl + '\n')
    lf.close()

    priors, nuisance, mq, tex, parnames, nparams, nchains = common.load_chains_and_model_details(wdir)
    print('File %s loaded.' % inifile)
    return model, datapoints, parnames, nparams, nchains, priors, len(nuisance), mq, tex

def logposterior(X, datapoints, parnames, priors, model, fixed={}, beta=1):
    return likelihood.compute_logposterior(datapoints, collections.OrderedDict(zip(parnames,tuple(X))), fixed, priors, model, beta=beta) 

def MetropolisHastings(I, wdir, N, args, Q, S, list_last_state=None):
    np.random.seed()
    datapoints, priors, parnames, nparams, Fixed, model = args
    
    with open(os.path.join(wdir, 'lastlinechain%i.txt' % (I+1)), 'r') as f:
        lastline = f.readline()

    chain_size = common.readint(os.path.join(wdir, 'previous%i.txt' % (I+1)))
    X0 = lastline.strip('\n').split(',')
    Xt = [float(x) for x in X0[:nparams]]
    lpXt = float(X0[nparams])
    if not isinstance(Xt, list):  # 1-D case
        Xt = [Xt,]
    lines_this_run = []
    accepted_moves = common.readint(os.path.join(wdir, 'accepted_moves_%i.txt' % (I+1)))
    if lpXt == 0.:
        lpXt = logposterior(Xt, datapoints, parnames, priors, model, fixed=Fixed)[0]
    for t in range(N):
        T = t+1 + chain_size
        #Y = Q(Xt,S).rvs() # drawing Y from ~ Q(Y; Xt) with scipy.stats
        Y = Q(Xt, S) # drawing Y from ~ Q(Y; Xt) with numpy
        lpY = logposterior(Y, datapoints, parnames, priors, model, fixed=Fixed)[0]
        q = 1. if lpY > lpXt else np.exp(lpY - lpXt)
        #q = min(1, np.exp(lpY - lpXt))
        # * Q(Y,S).pdf(Xt)/Q(Xt,S).pdf(Y)) #* np.prod([dpar[var] for var in parnames])**-1 ...
        # Metropolis-Hastings
        ### the proposal/kernel distribution Q I'm using is symmetric, then the second ratio should always be 1 and that's fine. Remember to include the calculation of the second ratio if I eventually use an asymmetrical function Q.
        #original: q = posterior(Y)*Q(Y,S).pdf(Xt)/(posterior(Xt)*Q(Xt,S).pdf(Y))
        r = np.random.uniform() #(0,1)
        if r <= q:
            # A new point has been accepted. 
            Xt = Y 
            lpXt = lpY
            accepted_moves += 1

        lines_this_run.append(build_line_MCMC(Xt, lpXt))

    if list_last_state:
        list_last_state[I] = np.array(Xt)

    write_compressed(lines_this_run, wdir, 'reducedchain%i.txt' % (I+1), 'lastlinechain%i.txt' % (I+1))
    common.saveint(os.path.join(wdir, 'accepted_moves_%i.txt' % (I+1)), accepted_moves)
    common.saveint(os.path.join(wdir, 'previous%i.txt' % (I+1)), T)

def write_compressed(lines, wdir, chainfile, lastlinefile):
    with open(os.path.join(wdir, chainfile), 'a') as f:
        i = 0
        while i < len(lines):
            line = lines[i]
            g = 0
            while i < len(lines) and lines[i] == line:
                g += 1
                i += 1
            f.write(', '.join([str(L) for L in line] + [str(g),]) + '\n')
            
    with open(os.path.join(wdir, lastlinefile), 'w') as f:
        f.write(', '.join([str(L) for L in lines[-1]] + ['1']) + '\n')

def WalkAdapt(T, chain_mean, Xt, Sig, q, theta, nparams=None, alpha=0.7):
    gamma_n = T**(-alpha)
    chain_mean *= (1 - gamma_n)
    chain_mean += gamma_n * np.array(Xt)
    M = np.array(Xt) - chain_mean
    Sig = (1 - gamma_n) * Sig + gamma_n * np.dot(M.transpose(), M)
    #print('S[%i]' % (I+1), list(zip(parnames, np.sqrt(S))))
    theta += gamma_n * (q - 0.234)
    try:
        assert ~np.isnan(theta)
    except AssertionError:
        print('assertion error, theta is nan')
        print('gamma_n', gamma_n)
        print('q', q)
        print('T', T)
        raise
    if nparams is None:
        S = np.exp(2*theta) * Sig
    else:
        S = 2.38**2/nparams * Sig
    return chain_mean, Sig, theta, S, gamma_n

def GetChainSig(wdir, I, S):
    try:
        Sig = np.loadtxt(os.path.join(wdir, 'Sig%i.txt' % (I+1)))
    except IOError:
        Sig = S
    return Sig

def GetChainMean(wdir, I, nparams):
    try:
        chain_mean = np.loadtxt(os.path.join(wdir, 'chain_mean%i' % (I+1)))
    except IOError:
        try:
            # PT mode
            chain = np.loadtxt(os.path.join(wdir, 'PTchain%i.txt' % (I+1)), delimiter=',', ndmin=2)
            chain_mean = [np.average(chain[:,i], weights=chain[:,-1]) for i in range(nparams)]
        except IOError:
            # MCMC mode
            chain = MCMC_chains.readchain_seq(wdir, I)
            chain_mean = [chain[:,i].mean() for i in range(nparams)]

        chain_mean = np.array(chain_mean)

    return chain_mean

def WalkAdaptSave(wdir, I, S, sig, cm, theta):
    np.savetxt(os.path.join(wdir, 'theta%i.txt' % (I+1)), [theta,])
    np.savetxt(os.path.join(wdir, 'chain_mean%i.txt' % (I+1)), cm)
    np.savetxt(os.path.join(wdir, 'Sig%i.txt' % (I+1)), sig)
    np.savetxt(os.path.join(wdir, 'Sm%i.txt' % (I+1)), S)

def load_chain_state(I, wdir, nparams):
    with open(os.path.join(wdir, 'lastlinePTchain%i.txt' % (I+1)), 'r') as f:
        lastline = f.readline()
    X0 = lastline.strip('\n').split(',')
    X0 = [float(x) for x in X0[:-1]]
    return X0[:nparams], X0[nparams], X0[nparams+1] # last three are lpX and llX

def build_line(X, lpX, llX):
    aux = list(X)
    aux.extend([lpX, llX])
    return aux

def build_line_MCMC(X, lpX):
    X = list(X)
    X.append(lpX)
    return X

def line_to_state(line, nparams):
    Xt = line[:nparams]
    lpXt, llXt = line[nparams:]
    return Xt, lpXt, llXt

def manage_swap(
        shared_last_lines, q_swapped, chain_advanced, chain_completed,
        shared_gamma_n, shared_theta,
        shared_adapt, nchains, args, betas, wdir,
        lp_with_beta_below, lp_with_beta_above
        ):
    np.random.seed()

    proposed_swaps = common.readint(os.path.join(wdir, 'proposed_swaps.txt'))
    accepted_swaps = common.readint(os.path.join(wdir, 'accepted_swaps.txt'))
    loops = 0

    datapoints, priors, parnames, nparams, Fixed, model = args

    while not chain_completed.value:

        if not chain_completed.value:
            
            for m in range(nchains.value):
                chain_advanced[m].wait()
            #print('chains advanced. Will now propose swap', end='')

            for m in range(nchains.value):
                chain_advanced[m].clear()

        if not chain_completed.value:
            proposed_swaps += 1
            i = np.random.randint(nchains.value-1)
            accswap = RandomSwap(i, i+1, shared_last_lines, betas, args)
            #i, j = np.random.choice(nchains.value, size=2, replace=False)
            #accswap = RandomSwap(i, j, shared_last_lines, betas, args)
            accepted_swaps += accswap

            if shared_adapt.value: 
                # Adaptive PT 4th step: Temperature Scheme Adaptation
                T = [1.,]
                for m in range(nchains.value-1):
                    num = lp_with_beta_above[m]
                    den = lp_with_beta_below[m+1]
                    if accswap:
                        if m in [i, i+1]:
                            Xt, _, _ = line_to_state(shared_last_lines[m], nparams)
                            num = logposterior(Xt, datapoints, parnames, priors, model, fixed=Fixed, beta=betas[m+1])[0]
                        if m+1 in [i, i+1]:
                            Xtmp1, _, _ = line_to_state(shared_last_lines[m+1], nparams)
                            den = logposterior(Xtmp1, datapoints, parnames, priors, model, fixed=Fixed, beta=betas[m])[0]

                    xi = 1. if num > den else np.exp(num - den)
                    T.append(T[m] + 1./betas[m+1] - 1./betas[m] + shared_gamma_n[m] * (xi - 0.234))

                for m in range(nchains.value):
                    betas[m] = 1./T[m]

                np.savetxt(os.path.join(wdir, 'betas.txt'), betas)

                #print('new betas', len(betas), ', '.join(["%.3e" % beta for beta in betas]))

                # Adaptive PT 5th step: Number of Temperatures Adaptation
                #print(2.38/np.sqrt(nparams), [np.exp(shared_theta[m]) for m in range(nchains.value)])
                satisfying_condition = [m for m in range(nchains.value) if \
                        np.exp(shared_theta[m]) >= 2.38/np.sqrt(nparams)]
                try:
                    #print('list', satisfying_condition)
                    Lmax = min(satisfying_condition)+1
                except ValueError:
                    pass
                else:
                    for m in range(Lmax, nchains.value):
                        betas[m] = 0
                    #betas = betas[:Lmax]
                    np.savetxt(os.path.join(wdir, 'betas.txt'), betas[:Lmax])
                    # delete chains above Lmax
                    for j in range(Lmax, nchains.value)[::-1]:
                        nchains.value = remove_bad_chains.deletechain(wdir, j+1) #this already updates nchains.txt
                    #print('Now with %i chains' % nchains.value)

            q_swapped.set()

    common.saveint(os.path.join(wdir, 'accepted_swaps.txt'), accepted_swaps)
    common.saveint(os.path.join(wdir, 'proposed_swaps.txt'), proposed_swaps)
    if proposed_swaps > 0:
        np.savetxt(os.path.join(wdir, 'swaps_ratio.txt'), [accepted_swaps/proposed_swaps,], fmt='%.3f')
    else:
        np.savetxt(os.path.join(wdir, 'swaps_ratio.txt'), [0,], fmt='%.3f')

def advance_chain_MH(
        list_steps, bool_propose, bool_adapting, q_swapped, shared_last_lines,
        shared_gamma_n, shared_theta, shared_chain_mean, shared_Sig, shared_adapt,
        lp_with_beta_below, lp_with_beta_above,
        chain_advanced, chain_completed, m, nchains, betas, wdir, Q, S,
        datapoints, nparams, parnames, priors, Fixed, model
        ):

    np.random.seed()
    lines_this_run = []
    acc = common.readint(os.path.join(wdir, 'accepted_states_%i.txt' % (m+1)))

    try:
        T = common.readint(os.path.join(wdir, 'total_steps_%i.txt' % (m+1)))
    except IOError:
        T = 0
    for steps, swap_this_time, adapt in zip(list_steps, bool_propose, bool_adapting):
        if m < nchains.value:
            q_swapped.clear()
            chain_advanced[m].clear()
            if len(lines_this_run) > 0:
                lines_this_run[-1] = list(shared_last_lines[m])
            Xt, lpXt, llXt = line_to_state(shared_last_lines[m], nparams)

            shared_adapt.value = adapt

            if steps > 0:
                for _ in range(steps):
                    Y = Q(Xt, S[m])
                    lpY, llY = logposterior(Y, datapoints, parnames, priors, model, fixed=Fixed, beta=betas[m])
                    q = 1. if lpY > lpXt else np.exp(lpY - lpXt)
                    r = np.random.uniform() #(0,1)
                    if r <= q:
                        # accepts new point
                        Xt, lpXt, llXt = Y, lpY, llY
                        acc += 1

                    T += 1
                    if adapt:
                        shared_chain_mean[m], shared_Sig[m], shared_theta[m], possible_S, shared_gamma_n[m] = WalkAdapt(
                            T, shared_chain_mean[m], Xt, shared_Sig[m], q, shared_theta[m]
                            )

                        if np.any(np.isnan(possible_S)):
                            pass
                            # didn't update S[m]
                        else:
                            S[m] = possible_S

                        if m > 0:
                            lp_with_beta_below[m] = logposterior(Xt, datapoints, parnames, priors, model, fixed=Fixed, beta=betas[m-1])[0]
                        try:
                            lp_with_beta_above[m] = logposterior(Xt, datapoints, parnames, priors, model, fixed=Fixed, beta=betas[m+1])[0]
                        except IndexError:
                            pass

                    lines_this_run.append(build_line(Xt, lpXt, llXt))

            shared_last_lines[m] = build_line(Xt, lpXt, llXt)

            ##chain_advanced[m].set()
            #print('Chain %i advancing %i steps' % (m+1, steps))

            if swap_this_time:
                chain_advanced[m].set()
                # wait other chains finish and swapping happen
                q_swapped.wait()

        else:
            chain_advanced[m].set()
            break
    
    common.saveint(os.path.join(wdir, 'total_steps_%i.txt' % (m+1)), T)
    chain_advanced[m].set()

    if m < nchains.value:
        #print('Chain %i finished' % (m+1))
        chain_completed.value = True
        common.saveint(os.path.join(wdir, 'accepted_states_%i.txt' % (m+1)), acc)

        write_compressed(lines_this_run, wdir, 'PTchain%i.txt' % (m+1), 'lastlinePTchain%i.txt' % (m+1))

def RandomWalkPhase(
        shared_last_lines, nchains, wdir, args, betas,
        shared_gamma_n, shared_theta, shared_chain_mean, shared_Sig, shared_adapt,
        RandomWalkSteps, SwapInBetween, IsAdapting, q_swapped, chain_advanced, 
        chain_completed, Q, S,
        lp_with_beta_below, lp_with_beta_above
        ):
    datapoints, priors, parnames, nparams, Fixed, model = args
    jobs = []
    for m in range(nchains.value):
        Xt, lpXt, llXt = load_chain_state(m, wdir, nparams)
        if lpXt == 0. or llXt == 0.:
            lpXt, llXt = logposterior(Xt, datapoints, parnames, priors, model, fixed=Fixed, beta=betas[m])
        shared_last_lines[m] = build_line(Xt, lpXt, llXt)
        jobs.append(
                multiprocessing.Process(
                    target = advance_chain_MH, 
                    args = (
                        RandomWalkSteps, SwapInBetween, IsAdapting, q_swapped,
                        shared_last_lines, 
                        shared_gamma_n, shared_theta, shared_chain_mean, shared_Sig,
                        shared_adapt, lp_with_beta_below, lp_with_beta_above,
                        chain_advanced, chain_completed, m, nchains,
                        betas, wdir, Q, S, datapoints, nparams, parnames,
                        priors, Fixed, model
                        )
                    )
                )

    return jobs
        
def RandomSwap(i, j, shared_last_lines, betas, args):
    datapoints, priors, parnames, nparams, Fixed, model = args
    Xti, lpXti, llXti = line_to_state(shared_last_lines[i], nparams)
    Xtip1, lpXtip1, llXtip1 = line_to_state(shared_last_lines[j], nparams)
    num1 = logposterior(Xtip1, datapoints, parnames, priors, model, fixed=Fixed, beta=betas[i])
    num2 = logposterior(Xti, datapoints, parnames, priors, model, fixed=Fixed, beta=betas[j])
    num = num1[0] + num2[0]
    den = lpXti + lpXtip1
    r_swap = 1 if num > den else np.exp(num - den)
    U2 = np.random.uniform() #(0,1)
    if U2 <= r_swap:
        # accept the proposed swap
        shared_last_lines[i] = build_line(Xtip1, *num1)
        shared_last_lines[j] = build_line(Xti, *num2)
        return 1
    else:
        return 0
        
def ParallelTempering(wdir, N, nchains, args, Q, S, ns, betas, adapt=0, free_random_walk=0):
    np.random.seed()

    N -= free_random_walk + adapt
    assert N >= 0
    if N > 0:
        sn = 1/ns
        U = np.random.uniform(size=N)
        indices_propose_swap = np.flatnonzero(np.where(U <= sn, 1, 0))
        #try:
        #    swaps_happen = np.loadtxt(os.path.join(wdir, 'swaps_happen.txt'), dtype=int)
        #except IOError:
        #    swaps_happen = np.array([])
        #swaps_happen = np.concatenate([swaps_happen, indices_propose_swap])
        #np.savetxt(os.path.join(wdir, 'swaps_happen.txt'), swaps_happen, fmt="%i")

        indices_propose_swap = np.concatenate([[0], indices_propose_swap, [N]])
        n_iter_between_swaps = np.diff(indices_propose_swap)
        n_iter_between_swaps = n_iter_between_swaps[n_iter_between_swaps > 0]
    else:
        n_iter_between_swaps = np.ones(0, int)
    n_iter_between_swaps = np.concatenate([np.ones(adapt, int), n_iter_between_swaps])
    if free_random_walk:
        n_iter_between_swaps = np.concatenate([[free_random_walk,], n_iter_between_swaps])
    APT_burnin = free_random_walk, adapt
    shared_adapt = multiprocessing.Value(ctypes.c_bool, False)
    # This avoids 0 steps and empty lastlinePTchains or repetition of
    # lastlinePT on complete_chains by ignoring swap
    # proposals before propagation of the chains
    bool_propose = np.isreal(n_iter_between_swaps)
    bool_adapting = ~np.ones_like(bool_propose, bool)

    bool_propose[0] = int(not bool(free_random_walk))
    if N > 0:
        bool_propose[-1] = False
    bool_adapting[int(bool(free_random_walk)):int(bool(free_random_walk))+adapt] = True

    man = multiprocessing.Manager()
    shared_last_lines = man.list([])
    for _ in range(nchains.value):
        shared_last_lines.append([])
    chain_advanced = [multiprocessing.Event() for _ in range(nchains.value)]
    q_swapped = multiprocessing.Event()
    chain_completed = multiprocessing.Value(ctypes.c_bool, False)
    shared_gamma_n = multiprocessing.Array('d', np.zeros(nchains.value))
    #shared_eta = multiprocessing.Array('d', np.zeros(nchains.value))
    nparams = args[3]
    shared_theta = multiprocessing.Array('d', np.ones(nchains.value)* np.log(0.8*2.38/np.sqrt(nparams)))
    lp_with_beta_below = multiprocessing.Array('d', np.zeros(nchains.value))
    lp_with_beta_above = multiprocessing.Array('d', np.zeros(nchains.value))
    list_chain_means = [GetChainMean(wdir, m, nparams) for m in range(nchains.value)]
    list_Sigs = [GetChainSig(wdir, m, S) for m in range(nchains.value)]
    shared_chain_mean = man.list(list_chain_means)
    shared_Sig = man.list(list_Sigs)

    swap_manager = multiprocessing.Process(
            target = manage_swap,
            args = (
                shared_last_lines, q_swapped, chain_advanced, chain_completed,
                shared_gamma_n, shared_theta,
                shared_adapt, nchains, args, betas, wdir,
                lp_with_beta_below, lp_with_beta_above
                )
            )

    jobs = RandomWalkPhase(
        shared_last_lines, nchains, wdir, args, betas,
        shared_gamma_n, shared_theta, shared_chain_mean, shared_Sig, shared_adapt,
        n_iter_between_swaps, bool_propose, bool_adapting, q_swapped, chain_advanced, 
        chain_completed, Q, S,
        lp_with_beta_below, lp_with_beta_above
        )
        
    try: 
        swap_manager.start()
        for j in jobs:
            j.start()

        for j in jobs:
            j.join()
        swap_manager.join()

    except:
        pass
    else:
        proposed_states = common.readint(os.path.join(wdir, 'proposed_states.txt'))
        proposed_states += n_iter_between_swaps.sum()
        common.saveint(os.path.join(wdir, 'proposed_states.txt'), proposed_states)
        if free_random_walk + adapt > 0:
            for m in range(nchains.value):
                WalkAdaptSave(wdir, m, S[m], shared_Sig[m], shared_chain_mean[m], shared_theta[m])
        for m in range(nchains.value):
            acc = common.readint(os.path.join(wdir, 'accepted_states_%i.txt' % (m+1)))
            np.savetxt(os.path.join(wdir, 'accept_ratio_%i.txt' % (m+1)), [acc/proposed_states,], fmt="%.3f")

    return APT_burnin

#def backup_everything(wdir):
#    return shutil.make_archive('restore', 'zip', root_dir=os.path.join(wdir, '..'), base_dir=wdir.strip(os.path.sep).split(os.path.sep)[-1])
#
#def restore_everything(wdir, archive):
#    flist = os.listdir(wdir)
#    for ffl in flist:
#        os.remove(os.path.join(wdir, ffl))
#    os.rmdir(wdir)
#    os.mkdir(wdir)
#    zfile = zipfile.ZipFile(archive)
#    for name in zfile.namelist():
#        zfile.extract(name, os.path.join(wdir, '..'))
#    zfile.close()
#    os.remove(archive)

def mq_to_S(mq, parnames, beta=1.):#, priors):
    # absolute mq (sigma)
    S = np.array([mq[par]**2/beta for par in parnames])
    #S = np.array([(mq[par] * priors[par].interval_size)**2 for par in parnames])
    return np.diag(S)

def compare_proposals(accp, prevaccp, desired):
    accmin, accmax = desired
    Nacc = np.count_nonzero([a for a in accp if accmin < a < accmax])
    Nprev = np.count_nonzero([a for a in prevaccp if accmin < a < accmax])
    return Nacc, Nprev

#def status_accept(accp, desired):
#    accmin, accmax = desired
#    above = accp - accmax
#    above = np.array(above * (above>0)).sum()
#    below = accmin - accp
#    below = np.array(below * (below>0)).sum()
#    return above - below

def matrixplot(M, wdir):
    fig, ax = plt.subplots()
    ax.imshow(common.cov_to_corr(M))
    fig.savefig(os.path.join(wdir, 'Sm.pdf'))

def recalibrate(nchains, nparams, wdir, LLC, Sigma, N, theta, X, mu):
    #f = [MCMC_chains.readchain_seq(wdir, i) for i in range(nchains)]
    #N, f = MCMC_chains.truncate(f)
    #combo_chains = MCMC_chains.combine_chains_for_each_parameter(
    #        f, N//2, nchains, nparams)

    #S = np.cov(combo_chains)
    ##matrixplot(S, wdir)

    #pdb.set_trace()
    gamma = N**-0.6

    for i in range(nchains):
        mu[i] = (1 - gamma) * mu[i] + gamma * X[i]

    Xmu = X[0] - mu[0]
    Xmu = np.array(Xmu, ndmin=2)
    Sigma = (1 - gamma) * Sigma + gamma * np.dot(Xmu.transpose(), Xmu)

    """
    # Method 1
    S = 5.6644 / nparams * Sigma
    """

    # Method 2
    #pdb.set_trace()
    eta = LLC[0]
    theta += gamma * (eta - 0.234)
    S = np.exp(2*theta) * Sigma

    np.savetxt(os.path.join(wdir, 'Sm.txt'), S)
    return S, Sigma, mu, theta

def MCMCmain(workingdir, Nsteps, step=20, lastfew_p=5, MCMClimit=np.inf, checkafter=7200, Fixed={}, plot_histograms=True, adaPT=0, args=None):

    # MCMC variation
    with open(os.path.join(workingdir, 'mode.txt'), 'r') as modef:
        mode = modef.readline().strip()
        
    if args:
        CustomFixed = common.lookarg1list('Fixed=', args)
        if CustomFixed:
            dictfixed = collections.OrderedDict()
            for cfixed in CustomFixed:
                par, value = cfixed.split(':')
                dictfixed[par] = float(value)
            CustomFixed = collections.OrderedDict(dictfixed)
        Fixed = CustomFixed or Fixed

        adaPT = common.lookarg1list('adapt=', args, instance=int) or adaPT

        if mode == 'MCMC':
            # periodic convergence checks are made each "checkafter" hours, minutes or
            # seconds. Just include 2h, 30min or 30sec (useful for tests) in the
            # arguments. If more than one is specified, the program will prefer hours
            # over minutes over seconds.
            checkafter = common.find_timestring_convert_to_seconds(args) or checkafter

            # this sets the number of intermediate steps when monitoring convergence,
            # for k between 0 and n. Convergence diagnostics considers only the last
            # few values of k, for faster analysis, so this number can also be set
            step = common.lookarg1('GRstep=', args, instance=int) or step
            step = max(2, step)
            lastfew_p = common.lookarg1('lastfew=', args, instance=int) or lastfew_p

            # MCMClimit, in case one wants to perform a fixed number of steps
            MCMClimit = common.lookarg1('limit=', args, instance=int) or MCMClimit
            
            # tolerance for standard MCMC
            tol = common.lookarg1('tol', args, instance=float, optask='Please specify the tolerance for convergence: ')

        elif mode == 'PT':
            MCMClimit = common.lookarg1('limit=', args, instance=int, optask='Type the maximum number of steps: ')

    free_random_walk = 0

    if adaPT:
        if len(adaPT) == 1:
            free_random_walk = 0
            adaPT = adaPT[0]
        else:
            free_random_walk, adaPT = adaPT[:2]

    find_ini = common.getfilelist(workingdir, 'ini')[0]
    inifile = os.path.join(workingdir, find_ini)
    model, datapoints, parnames, nparams, nchains, priors, nnuis, mq, tex = load_ini(workingdir, inifile)
    theta = 0.
    try:
        S = np.loadtxt(os.path.join(workingdir, 'Sm.txt'))
    except IOError:
        S = mq_to_S(mq, parnames) #, priors)
    Sigma = np.array(S) * nparams/5.6644

    print('')
    print('The following datasets will be used:', ', '.join(datapoints))
    print('')

    p_args = (datapoints, priors, parnames, nparams, Fixed, model)

    Q = np.random.multivariate_normal

    backup_fullpath = os.path.join(workingdir, 'backup chains')
    if not os.path.isdir(backup_fullpath):
        os.mkdir(backup_fullpath)

    totaliterations = 0
    hlast = max(1, step//lastfew_p)
    hatRp = 2*np.ones(hlast)
    try:
        counter = common.readint(os.path.join(workingdir, 'counter.txt'))
    except IOError:
        counter = 0
    totaltime = 0
    try:
        cumulatedtime = float(np.loadtxt(os.path.join(workingdir, 'cumulatedtime.txt')))
    except IOError:
        cumulatedtime = 0.

    last_update_N = 0

    if mode == 'MCMC':
        print('Initiating MCMC...')
        if adaPT:
            print('Adaptive MCMC burn-in: %i' % ((free_random_walk + adaPT) * Nsteps))
        orignchains = int(nchains)

        # standard MCMC
        while (np.any(abs(hatRp[-hlast:]-1) > tol) and last_update_N < MCMClimit):# totaliterations < MCMClimit):

            itime = time()
            if adaPT and (free_random_walk <= counter < free_random_walk + adaPT * Nsteps):
                real_Nsteps = 1
            else:
                for i in range(nchains):
                    shutil.copy2(os.path.join(workingdir, 'reducedchain%i.txt' % (i+1)), backup_fullpath)
                    shutil.copy2(os.path.join(workingdir, 'previous%i.txt' % (i+1)), backup_fullpath)
                    shutil.copy2(os.path.join(workingdir, 'lastlinechain%i.txt' % (i+1)), backup_fullpath)
                    if os.path.isfile(os.path.join(workingdir, 'accepted_moves_%i.txt' % (i+1))):
                        shutil.copy2(os.path.join(workingdir, 'accepted_moves_%i.txt' % (i+1)), backup_fullpath)
                if os.path.isfile(os.path.join(workingdir, 'llc.txt')):
                    shutil.copy2(os.path.join(workingdir, 'llc.txt'), backup_fullpath)
                shutil.copy2(os.path.join(workingdir, 'nchains.txt'), backup_fullpath)
                shutil.copy2(os.path.join(workingdir, 'chains.txt'), backup_fullpath)
                real_Nsteps = Nsteps

            manag = multiprocessing.Manager()
            X = manag.list(range(nchains))
            jobs = [multiprocessing.Process(
                target=MetropolisHastings, 
                args=(i, workingdir, real_Nsteps, p_args, Q, S),
                kwargs = {'list_last_state': X if (adaPT and (free_random_walk <= counter < free_random_walk + adaPT * Nsteps)) else None}
                #kwargs = {'adapt': adaPT and free_random_walk <= counter < adaPT}
                ) for i in range(nchains)]

            for j in jobs:
                j.start()

            for j in jobs:
                j.join()

            LLC = []
            for i in range(nchains):
                accepted_moves = common.readint(os.path.join(workingdir, 'accepted_moves_%i.txt' % (i+1)))
                total_moves = common.readint(os.path.join(workingdir, 'previous%i.txt' % (i+1)))
                #if i == 0:
                #    print('{0}/{1}'.format(accepted_moves, total_moves))
                LLC.append(accepted_moves/total_moves)

            np.savetxt(os.path.join(workingdir, 'llc.txt'), LLC, fmt="%.5f")

            if adaPT and free_random_walk <= counter < free_random_walk + adaPT * Nsteps:
                #print([llc.__format__('.2f') for llc in LLC])
                try:
                    mu
                except NameError:
                    f = [MCMC_chains.readchain_seq(workingdir, i) for i in range(nchains)]
                    _, f = MCMC_chains.truncate(f)
                    mu = []
                    #X = []
                    for F in f:
                        mu.append(np.mean(F, axis=0)[:nparams])
                        #X.append(F[-1][:nparams])

                #pdb.set_trace()
                S, Sigma, mu, theta = recalibrate(nchains, nparams, workingdir, LLC, Sigma, free_random_walk * Nsteps + counter - free_random_walk + 1, theta, X, mu)

            counter += 1
            ftime = time()
            iterationtime = ftime-itime
            totaltime += iterationtime
            #print('Iteration %i with %i steps, %i chains; in %s, on %s.' % (counter, real_Nsteps, nchains, common.printtime(iterationtime), ctime()), end=' ')
            if real_Nsteps > 1 or (real_Nsteps + last_update_N) % Nsteps == 0:
                print('i %i, %i steps, %i ch; %s, %s.' % (counter, real_Nsteps + last_update_N, nchains, common.printtime(iterationtime * (1 if real_Nsteps > 1 else Nsteps)), ctime()), end=' ')
            nextcheck = checkafter-totaltime
            last_update_N += real_Nsteps
            if nextcheck > 0.5 * iterationtime and last_update_N < MCMClimit:
                if real_Nsteps > 1 or last_update_N % Nsteps == 0:
                    print('Next: ~%s.' % common.printtime(nextcheck))
                    #print('Next convergence check in ~%s.' % common.printtime(nextcheck))
                    #print(S)
            else:
                if real_Nsteps > 1 or last_update_N % Nsteps == 0:
                    print('Checking now...')
                    #print('Checking convergence now...')
                prev_nchains = int(nchains)
                nchains = remove_bad_chains.deletebadchains(workingdir, args=args)
                if nchains < prev_nchains:
                    initialize_chains.redraw_initial_states(workingdir, ['originalchains.txt', 'chains.txt'], [('b', 2, None, 0), ('', 5, 'r', 0.5)], parnames, nparams, priors, [orignchains, nchains], tex, 'deleted_states', [True, False])
                cumulatedtime += totaltime
                np.savetxt(os.path.join(workingdir, 'cumulatedtime.txt'), (cumulatedtime,))
                np.savetxt(os.path.join(workingdir, 'counter.txt'), (counter,), fmt="%i")

                # MCMC_chains
                aitime = time()
                f, combobins, n, _, _, _, _ = MCMC_chains.analyze_chains(workingdir, wDE_list=None, plot_sequences=False, ACF=False, THIN=1, args=args)

                #if lastfew_p > 0:
                #    lf = -max(1, step//lastfew_p)
                #else:
                #    lf = 0
                lf = 0
                _, hatRp = MCMC_chains.GelmanRubin(f, n, "n%i" % n, nchains, nparams, workingdir, lastfew=lf, args=args)
                aftime = time()
                print('Total time for data analysis: %s.' % common.printtime(aftime - aitime))

                totaliterations = n
                print('After %s and %i steps, with %i chains,' % (common.printtime(cumulatedtime), totaliterations, nchains))
                timenow = ctime()
                #print('Eigenvalues:', collections.OrderedDict(zip(parnames, np.sqrt(eigenvalues))))
                print('Convergence %.2e achieved. Current time: %s.' % ((hatRp[-hlast:].mean()-1), timenow))
                with open(os.path.join(workingdir, "n%i" % n, 'convergence.txt'), 'a') as h:
                    h.write('\n')
                    h.write('Convergence hatRp-1: \t ' + ', '.join(["%.4e" % (Rp-1) for Rp in hatRp[-hlast:]]) + '\n')
                
                totaltime = 0

        if totaliterations < MCMClimit:
            out = '%.2e convergence achieved after %i steps.' % (tol, totaliterations)
            h = open(os.path.join(workingdir, "n%i" % n, 'convergence.txt'), 'a')
            h.write('\n')
            h.write(out + '\n')
            h.close()
            print('' )
            print(out)
            print(workingdir)
            print('')
        else:
            #out = "Distributions didn't converge after %i steps. Consider using a tolerance higher than %.2e" % (MCMClimit, tol)
            #print(out)
            #print('')
            print('Finished running %i steps' % MCMClimit)


        if plot_histograms:
            itime = time()
            drawhistograms.build_histograms([os.path.join(workingdir, "n%i" % n, 'results%i' % cb) for cb in combobins], args=args)
            ftime = time()
            print('Results plotted in %s.' % common.printtime(ftime - itime))

        
    elif mode == 'PT':
        print('Initiating Parallel Tempering...')
        try:
            counter = common.readint(os.path.join(workingdir, 'counter.txt'))
        except IOError:
            counter = 0
        duration_start = time()
        betas = np.loadtxt(os.path.join(workingdir, 'betas.txt'))
        ns = common.readint(os.path.join(workingdir, 'ns.txt'))
        # parallel tempering
        try:
            S = [np.loadtxt(os.path.join(workingdir, 'Sm%i.txt' % (m+1))) for m in range(nchains)]
        except IOError:
            S = [mq_to_S(mq, parnames, beta=betas[i]) for i in range(nchains)]
        manag = multiprocessing.Manager()
        S = manag.list(S)
        nchains = multiprocessing.Value('i', nchains)
        betas = multiprocessing.Array('d', betas)
        while last_update_N < MCMClimit:
            itime = time()
            #for m in range(nchains.value):
            #    shutil.copy2(os.path.join(workingdir, 'PTchain%i.txt' % (m+1)), backup_fullpath)
            #    shutil.copy2(os.path.join(workingdir, 'lastlinePTchain%i.txt' % (m+1)), backup_fullpath)

            frw = max(0, min(Nsteps, free_random_walk - last_update_N))
            ADAPT = min(adaPT % Nsteps, adaPT - frw - last_update_N)
            ADAPT = max(0, min(Nsteps - frw, adaPT + int(bool(last_update_N)) * free_random_walk - last_update_N))
            #print('frw, ADAPT', frw, ADAPT)
            APT_burnin = ParallelTempering(workingdir, Nsteps, nchains, p_args, Q, S, ns, betas, adapt=ADAPT, free_random_walk=frw)
            with open(os.path.join(workingdir, 'accept_ratio_1.txt'), 'r') as af:
                accept_ratio = af.readline().strip()
            with open(os.path.join(workingdir, 'swaps_ratio.txt'), 'r') as sf:
                swap_ratio = sf.readline().strip()

            ftime = time()
            iterationtime = ftime - itime
            totaltime += iterationtime
            counter += 1
            if np.any(np.array(APT_burnin)) > 0:
                print('Adaptive PT steps: free random walk: %i, adaptive: %i' % APT_burnin)
            print('i %i, %i of %i steps, %i ch; %s, ns %i, swap %s, accpt %s, %s.'
                    % (
                        counter, Nsteps + last_update_N, MCMClimit, nchains.value,
                        common.printtime(iterationtime), ns, swap_ratio,
                        accept_ratio, ctime()
                        )
                    )
            if counter % 10 == 0:
                for m in range(nchains.value):
                    with open(os.path.join(workingdir, 'accept_ratio_%i.txt' % (m+1)), 'r') as af:
                        accept_ratio = af.readline().strip()
                        print(accept_ratio, end=', ')
                print('')

            last_update_N += Nsteps

        duration_end = time()
        common.saveint(os.path.join(workingdir, 'counter.txt'), counter)

        print('Total elapsed time in Parallel tempering: %s' % common.printtime(duration_end - duration_start))
        common.saveint(os.path.join(workingdir, 'duration.txt'), duration_end - duration_start)

        import PT_chains
        itime = time()

        _, combobins, n, nparams, tex, parnames = PT_chains.analyze_chains(workingdir, bchain=1, args=args)

        ftime = time()
        print('Total time for data analysis: %s.' % common.printtime(ftime - itime))
        print('' )

        # Tells the program to plot or not the histograms in the end. If not
        # desired, include dontdraw in arguments
        plot_histograms = not common.lookarg('dontdraw', args)

        if plot_histograms:

            itime = time()
            for cb in combobins:
                drawhistograms.build_histograms([os.path.join(workingdir, "n%ib%i" % (n, 1), 'results%i' % cb)], args=args)
            ftime = time()
            print('Results plotted in %s.' % common.printtime(ftime - itime))
            print('')

    
    flist = os.listdir(backup_fullpath)
    for ffl in flist:
        os.remove(os.path.join(backup_fullpath, ffl))
    os.rmdir(backup_fullpath)


if __name__ == '__main__':

    # define number of steps and tolerance for convergence
    Nsteps_user = common.lookarg1('steps=', sys.argv, instance=int, optask='Please specify the number of steps in each passage in the MCMC loop: ')
    starting_point = common.lookarg1list('starting_point=', sys.argv, instance=float)

    print('Started on %s.' % ctime())

    # The first argument must be the .ini file or the folder with an previous
    # evaluation to be continued.
    if os.path.isdir(sys.argv[1]):
        workingdir = sys.argv[1]
    elif os.path.isfile(sys.argv[1]):

        mode = common.lookarg1('mode=', sys.argv) or 'MCMC'
        Nc, workingdir, parnames, nparams, tex, priors, _, plotstates = initialize_chains.readargs(sys.argv, mode)
        initialize_chains.register_mode(workingdir, mode)

        if mode == 'MCMC':
            initialize_chains.write_chains_files(workingdir, parnames, priors, Nc, starting_point=starting_point)
            initialize_chains.write_previous_files(workingdir, Nc)

            if plotstates:
                initialize_chains.redraw_initial_states(workingdir, ['originalchains.txt'], [('b', 2, None, 0)], parnames, nparams, priors, [Nc], tex, 'original_states', [True])

        elif mode == 'PT':
            initialize_chains.write_PTchains_files(workingdir, parnames, priors, Nc, args=sys.argv)

    MCMCmain(workingdir, Nsteps_user, args=sys.argv)

