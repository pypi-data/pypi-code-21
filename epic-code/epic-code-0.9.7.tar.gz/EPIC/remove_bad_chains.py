from __future__ import print_function
import sys
import os
import numpy as np
from EPIC import common

def removeline(N, wdir, filename):
    chainsfile = open(os.path.join(wdir, filename), 'r')
    lines = chainsfile.readlines()
    lines.pop(N) # first line is header
    chainsfile.close()

    chainsfile = open(os.path.join(wdir, filename), 'w')
    for line in lines:
        chainsfile.write(line)
    chainsfile.close()

def deletechain(wdir, N):

    with open(os.path.join(wdir, 'mode.txt'), 'r') as modef:
        mode = modef.readline().strip()
    nchains = common.readint(os.path.join(wdir, 'nchains.txt'))

    if mode == 'PT':
        filestodelete = [
                'PTchain', 
                'accepted_states_', 
                'lastlinePTchain',
                'accept_ratio_',
                'chain_mean',
                'total_steps_',
                'Sig',
                'Sm',
                'theta',
                ]
    else:
        filestodelete = [
                'reducedchain',
                'previous',
                'lastlinechain',
                'accepted_moves_',
                'chain_mean',
                'Sig',
                'Sm',
                'theta',
                ]

    for fileofchain in filestodelete:
        try:
            os.remove(os.path.join(wdir, fileofchain + '%i.txt' % N))
        except OSError:
            pass

        for i in range(N+1, nchains+1):
            try:
                os.rename(os.path.join(wdir, fileofchain + '%i.txt' % i), os.path.join(wdir, fileofchain + '%i.txt' % (i-1)))
            except:
                pass

    common.saveint(os.path.join(wdir, 'nchains.txt'), nchains-1)

    if mode == 'MCMC':
        removeline(N, wdir, 'chains.txt')
        removeline(N-1, wdir, 'llc.txt')

    return nchains-1

def deletebadchains(wdir, accplims=[0.1,0.5], args=False):
    if args:
        # define limits for acceptance rate. Chains with values outside this
        # interval will be removed from the analysis. Good values for acceptance
        # ratio are generally between 0.1 and 0.5.
        accplims = common.lookarg1list('accacc=', args, instance=float) or accplims
    
    accpmin, accpmax = accplims
    llc = list(np.loadtxt(os.path.join(wdir, 'llc.txt')))
    nchains = common.readint(os.path.join(wdir, 'nchains.txt'))

    for i in range(nchains)[::-1]:
        if not accpmin <= llc[i] <= accpmax:
            deletechain(wdir, i+1)
            print('Chain #%i removed (acc = %.4f).' % ((i+1), llc[i]) )
            llc.pop(i)

    np.savetxt(os.path.join(wdir, 'llc.txt'), llc, fmt="%.5f")

    return len(llc)

if __name__ == '__main__':
    wdir = sys.argv[1]
    N = common.lookarg1list('N=', sys.argv, instance=int)
    if N:
        N.sort()
        for n in N[::-1]:
            deletechain(wdir, n)
    else:
        accplims = common.lookarg1list('accacc=', sys.argv, instance=float)
        assert accplims
        deletebadchains(wdir, accplims)
