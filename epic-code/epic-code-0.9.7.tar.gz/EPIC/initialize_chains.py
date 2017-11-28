from __future__ import division
from __future__ import print_function
#import pdb
from EPIC import common
import os, sys, shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    input = input
except NameError:
    pass

UseTex = False
if UseTex:
    plt.rc('font',**{'family':'serif','serif':['cmr10']}) # 'Times'
    plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}', r'\usepackage{siunitx}']
    plt.rc('text', usetex=True)
plt.rcParams['axes.linewidth'] = 0.5
#plt.rcParams['text.latex.unicode'] = True
#plt.rcParams['font.serif'] = 'Palatino'
plt.rcParams['legend.fontsize'] = 'medium'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.major.width'] = 0.5
plt.rcParams['ytick.major.width'] = 0.5

def load_ini(inifile):
    lines = common.readfile(inifile)
    priors, nuisance, mq = common.lookprior(lines)
    tex = common.looktagstrings(lines, 'TEX')
    obsbles = common.looktagstrings(lines, 'DATA')
    return priors, nuisance, mq, tex, obsbles

def register_chains_and_model_details(wdir, priors, nuisance, mq, tex, parnames, nparams, nchains):
    pickle.dump(priors, open(os.path.join(wdir, 'priors.p'), 'wb'), 0)
    pickle.dump(nuisance, open(os.path.join(wdir, 'nuisance.p'), 'wb'), 0)
    pickle.dump(mq, open(os.path.join(wdir, 'mq.p'), 'wb'), 0)
    pickle.dump(tex, open(os.path.join(wdir, 'tex.p'), 'wb'), 0)
    pickle.dump(parnames, open(os.path.join(wdir, 'parnames.p'), 'wb'), 0)
    common.saveint(os.path.join(wdir, 'nparams.txt'), nparams)
    common.saveint(os.path.join(wdir, 'nchains.txt'), nchains)

def draw_initial_states(workingdir, chainsfile, pointstyle, grid, subplots, parnames, nparams, priors, nchains, tex, annotate=False):
    C = np.loadtxt(os.path.join(workingdir, chainsfile), delimiter=',')
    if nparams == 1:
        C = np.array([[c] for c in C])
    cor, radius, ec, lw = pointstyle
    
    indj = {}
    for i, var in enumerate(parnames):
        indj[var] = i
        
    for i in range(nparams*nparams):
        jx, jy = divmod(i, nparams)
        if jx > jy:
            subplots[jx][jy].scatter(C[:,indj[parnames[jy]]], C[:,indj[parnames[jx]]], c=cor, s=radius, edgecolor=ec, linewidths=lw)
            if annotate:
                for k in range(nchains):
                    subplots[jx][jy].annotate(
                            str(k+1), xy=(C[k,indj[parnames[jy]]], C[k,indj[parnames[jx]]]), xytext=(-2,-3),
                            fontsize=5,
                            textcoords = 'offset points', ha = 'right', va = 'bottom')
            subplots[jx][jy].tick_params(size=3)

            pmin, pmax = priors[parnames[jy]].vmin, priors[parnames[jy]].vmax
            intv = (pmax - pmin)/3
            imarg = intv/2
            subplots[jx][jy].set_xlim(pmin, pmax)
            subplots[jx][jy].set_xticks(np.linspace(pmin+imarg, pmax-imarg, num=3))

            pmin, pmax = priors[parnames[jx]].vmin, priors[parnames[jx]].vmax
            intv = (pmax - pmin)/3
            imarg = intv/2
            subplots[jx][jy].set_ylim(pmin, pmax)
            subplots[jx][jy].set_yticks(np.linspace(pmin+imarg, pmax-imarg, num=3))

        elif jx < jy:
            try:
                grid.delaxes(subplots[jx][jy])
            except KeyError:
                pass

        else:
            subplots[jx][jy].scatter(C[:,indj[parnames[jy]]], np.ones(nchains)*(priors[parnames[jx]].vmax+priors[parnames[jx]].vmin)/2, c=cor, s=radius, edgecolor=ec, linewidths=lw)
            subplots[jx][jy].tick_params(size=3, left='off', right='off')
            subplots[jx][jy].set_title(r'$' + tex[parnames[jx]] + '$') #, fontdict={'fontsize': 8})

    lastrowpar = parnames[nparams-1]
    pmin, pmax = priors[lastrowpar].vmin, priors[lastrowpar].vmax
    subplots[-1][-1].set_xlim(pmin, pmax)
    intv = (pmax - pmin)/3
    imarg = intv/2
    subplots[-1][-1].set_xticks(np.linspace(pmin+imarg, pmax-imarg, num=3))

    for i in range(nparams):
        subplots[-1][i].set_xlabel(r'$' + tex[parnames[i]] + '$')
    for i in range(1,nparams):
        subplots[i][0].set_ylabel(r'$' + tex[parnames[i]] + '$')

    subplots[0][0].set_yticklabels('')

    return grid, subplots

def readargs(args, mode):
    prefix = mode
    cfullname = common.lookarg1('cfullname', args)
    if cfullname:
        hora = '%s-%s' % (prefix, cfullname)
    else:
        hora = '%s-%s' % (prefix, common.define_time())
    cname = common.lookarg1('cname=', args)
    altfolder = common.lookarg1('altdir=', args)
    if not altfolder:
        try:
            altdir = open('altdir.txt', 'r')
            altfolder = altdir.readline().strip()
            altdir.close()
        except IOError:
            altfolder = False
    if cname:
        hora = '%s-%s' % (cname, hora)

    print(hora)

    plotstates = not common.lookarg('dontplotstates', args)

    inifile = common.lookarg('.ini', args) or input('Type in the name of the \'.ini\' file: ')
    inifile = common.assert_extension(inifile, 'ini')
    inidir = inifile[:-4]

    pardir = altfolder or os.path.abspath(os.pardir)

    if not os.path.isdir(os.path.join(pardir,inidir)):
        os.mkdir(os.path.join(pardir,inidir))

    workingdir = common.pasta(os.path.join(pardir,inidir), hora)
    shutil.copy2(inifile, workingdir)

    Nc = common.lookarg1('chains=', args, optask='Please specify the number of chains: ', instance=int)

    #priors, nuisance, mq, tex, obsbles = load_ini(inifile)
    priors, nuisance, mq, tex, _ = load_ini(inifile)
    parnames = list(priors.keys())
    nparams = len(parnames)
    #for obsname in obsbles.keys():
    #    if os.path.isdir(obsbles[obsname]):
    #        shutil.copytree(obsbles[obsname], os.path.join(workingdir, obsbles[obsname]))
    #    else:
    #        shutil.copy2(obsbles[obsname], workingdir)

    register_chains_and_model_details(workingdir, priors, nuisance, mq, tex, parnames, nparams, Nc)

    return Nc, workingdir, parnames, nparams, tex, priors, mq, plotstates

def write_PTchains_files(wdir, parnames, priors, Nc, betamax=10, betascale='log', args=None):
    if args:
        # propose a swap each ~ ns steps
        ns = common.lookarg1('nswap=', args, instance=int, optask='Please specify after how many steps should propose a swap: ')

        # custom array of temperatures
        betamax = common.lookarg1('betamax=', args, instance=int) or betamax
        betascale = common.lookarg1('betascale=', args) or betascale

    common.saveint(os.path.join(wdir, 'proposed_swaps.txt'), 0)
    common.saveint(os.path.join(wdir, 'accepted_swaps.txt'), 0)
    common.saveint(os.path.join(wdir, 'proposed_states.txt'), 0)
    for m in range(Nc):
        common.saveint(os.path.join(wdir, 'accepted_states_%i.txt' % (m+1)), 0)
    common.saveint(os.path.join(wdir, 'ns.txt'), ns)

    if betascale == 'log':
        betas = np.linspace(0, betamax, Nc)
        betas = 2**betas
        betas = 1/betas
    else:
        betas = np.linspace(1, betamax, Nc)
        betas = 1/betas

    np.savetxt(os.path.join(wdir, 'betas.txt'), betas)
    for i in range(Nc):
        with open(os.path.join(wdir, 'PTchain%i.txt' % (i+1)), 'w') as f:
            X0 = [np.random.normal(priors[var].ref, priors[var].interval_size/10) for var in parnames]
            #X0 = [np.random.uniform(priors[var].vmin, priors[var].vmax) for var in parnames]
            f.write(', '.join([str(x0) for x0 in X0] + ['0.', '0.', '1']) + '\n')
        shutil.copy2(os.path.join(wdir, 'PTchain%i.txt' % (i+1)), os.path.join(wdir, 'lastlinePTchain%i.txt' % (i+1)))

def write_chains_files(workingdir, parnames, priors, Nc, starting_point=None):
    g = open(os.path.join(workingdir,'originalchains.txt'), 'w')
    g.write('#'+ ', '.join([var for var in parnames]))
    g.write('\n')

    for i in range(Nc):
        common.saveint(os.path.join(workingdir, 'accepted_moves_%i.txt' % (i+1)), 1)
        f = open(os.path.join(workingdir,'reducedchain%i.txt' % (i+1)), 'w')
        #X0 = []
        #for var in parnames:
        #    s = 0.5 * priors[var].interval_size
        #    x = priors[var].vmax + 1
        #    while not(priors[var].vmin < x < priors[var].vmax):
        #        x = np.random.normal(priors[var].ref, s)
        #    X0.append(x)
        if starting_point:
            X0 = starting_point
        else:
            X0 = []
            for var in parnames:
                if hasattr(priors[var], 'mu'):
                    X0.append(np.random.normal(priors[var].mu, priors[var].sigma))
                else:
                    X0.append(np.random.uniform(priors[var].vmin, priors[var].vmax))

        f.write(', '.join([str(x0) for x0 in X0] + ['0.', '1']) + '\n')
        g.write(', '.join([str(x0) for x0 in X0]) + '\n')
        f.close()
        shutil.copy2(os.path.join(workingdir,'reducedchain%i.txt' % (i+1)), os.path.join(workingdir,'lastlinechain%i.txt' % (i+1)))
    g.close()

    shutil.copy2(os.path.join(workingdir, 'originalchains.txt'), os.path.join(workingdir, 'chains.txt'))

def write_previous_files(workingdir, Nc):
    for i in range(Nc):
        f = open(os.path.join(workingdir,'previous%i.txt' % (i+1)), 'w')
        f.write('1')
        f.close()

def redraw_initial_states(workingdir, chainsfiles, liststyles, parnames, nparams, priors, Nc, tex, pdfname, stamp_numbers):
    titlespace = 0.3
    grid, subplots = plt.subplots(nparams, nparams, sharex='col', sharey='row')
    grid.set_size_inches(nparams * 1.6, nparams * 1.6 + titlespace)
    if nparams == 1:
        subplots = [[subplots,],]

    for chainfile, style, nchains, annotate in zip(chainsfiles, liststyles, Nc, stamp_numbers):
        grid, subplots = draw_initial_states(workingdir, chainfile, style, grid, subplots, parnames, nparams, priors, nchains, tex, annotate)

    toppos=0.1
    #lateral = 1/nparams - 0.02
    #lateral = 0.02
    grid.tight_layout()
    grid.subplots_adjust(top=1-toppos)
    #grid.subplots_adjust(left=lateral)
    #grid.subplots_adjust(right=1+lateral)
    grid.subplots_adjust(hspace=0.0)
    grid.subplots_adjust(wspace=0.0)
    grid.suptitle('Initial states', fontsize=24)
    grid.savefig(os.path.join(workingdir, "%s.pdf" % pdfname))
    if __name__ == '__main__':
        print('File %s.pdf saved.' % pdfname)

def register_mode(workingdir, mode):
    with open(os.path.join(workingdir, 'mode.txt'), 'w') as modef:
        modef.write(mode)

if __name__ == '__main__':

    mode = common.lookarg1('mode=', sys.argv) or 'MCMC'
    Nc, workingdir, parnames, nparams, tex, priors, _, plotstates = readargs(sys.argv, mode)
    register_mode(workingdir, mode)
    starting_point = common.lookarg1list('starting_point=', sys.argv, instance=float)

    if mode == 'MCMC':
        write_chains_files(workingdir, parnames, priors, Nc, starting_point=starting_point)
        write_previous_files(workingdir, Nc)
        if plotstates:
            redraw_initial_states(workingdir, ['originalchains.txt'], [('b', 2, None, 0)], parnames, nparams, priors, [Nc], tex, 'original_states', [True])

    elif mode == 'PT':

        write_PTchains_files(workingdir, parnames, priors, Nc, args=sys.argv)

