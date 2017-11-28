import sys
import os

if __name__ == '__main__':
    
    wdir = sys.argv[1] 
    with open(os.path.join(wdir, 'mode.txt'), 'r') as modef:
        mode = modef.readline().strip()

    if mode == 'MCMC':
        from EPIC import MCMC_chains
        MCMC_chains.initialize(sys.argv)
    elif mode == 'PT':
        from EPIC import PT_chains
        PT_chains.initialize(sys.argv)
