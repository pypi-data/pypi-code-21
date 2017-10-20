from datetime import datetime
from pathlib import Path
from matplotlib.pyplot import figure,subplots
from matplotlib.dates import DateFormatter,MinuteLocator, SecondLocator
from matplotlib.colors import LogNorm
#
from . import ISRPARAM


def timelbl(time,ax,tctime):
    if time.size<200:
        ax.xaxis.set_minor_locator(SecondLocator(interval=10))
        ax.xaxis.set_minor_locator(SecondLocator(interval=2))
    elif time.size<500:
        ax.xaxis.set_minor_locator(MinuteLocator(interval=10))
        ax.xaxis.set_minor_locator(MinuteLocator(interval=2))

    #ax.axvline(tTC[tReqInd], color='white', linestyle='--',label='Req. Time')
    ax.axvline(tctime['tstartPrecip'], color='red', linestyle='--', label='Precip. Start')
    ax.axvline(tctime['tendPrecip'], color='red', linestyle='--',label='Precip. End')

def plotisr(t,iono, pp, infile,cmap,tctime,sfmt,verbose):
    if t.size<2:  # need at least 2 times for pcolormesh
        return

    alt = iono.alt_km
#%% ISR plasma parameters
    for p,cn in zip(ISRPARAM,(LogNorm(),None,None,None)):
        _plot1d(pp.sel(isrparam=p).values,alt,p,sfmt,infile,tctime)
        fg =  figure(); ax = fg.gca()
        pcm = ax.pcolormesh(alt,t, pp.sel(isrparam=p).values, cmap = cmap, norm=cn)
        _tplot(t,tctime,fg,ax,pcm,sfmt,p,infile)
#%% ionosphere state parameters
    if verbose>0:
        for ind in ('n1','n2','n3','n4','n5','n6'):
            fg = figure(); ax=fg.gca()
            pcm = ax.pcolormesh(t,alt,iono[ind].values, cmap= cmap,norm=LogNorm(),
                                vmin=0.1,vmax=1e12)
            _tplot(t,tctime,fg,ax,pcm,sfmt,str(ind),infile)

def _tplot(t,tctime,fg,ax,pcm,sfmt,ttxt,infile):
    ax.autoscale(True,tight=True)
    ax.set_xlabel('time [UTC]')
    ax.set_ylabel('altitude [km]')
    ax.set_title(ttxt + '\n ' + infile)
    fg.colorbar(pcm,format=sfmt)
    timelbl(t,ax,tctime)
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax.tick_params(axis='both', which='both', direction='out', labelsize=12)

def _plot1d(y,z,name,sfmt,infile,tctime):
    if y.ndim==2: # all times, so pick last time
        y = y[-1,:]

    ax = figure().gca()
    ax.plot(y,z.values)
    ax.set_xlabel(name)
    ax.set_ylabel('altitude')
    ax.set_title(name+'\n'+infile)
    ax.grid(True)
    #ax.yaxis.set_major_formatter(sfmt)
    #timelbl(t,ax,tctime)
    #ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    #ax.autoscale(True)

def plotionoinit(d, pp, ifn):

    figure(1).clf()
    ax= figure(1).gca()
    for i in ['n'+str(j) for j in range(1,7)]:
        ax.plot(d[i], d.index, label=i)

    ax.set_xscale('log')
    ax.legend(loc='best')
#    #msis.plot(y='alt',x='n4',title=ifn,logx=True) # why doesn't this plot correctly?
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('n')
    ax.set_title('density')

    figure(2).clf()
    a2= figure(2).gca()
    for s in ('v1','v2','v3','ve','vm'):
        a2.plot(d[s], d.index, label=s)
    a2.set_xlabel('v')
    a2.set_ylabel('altitude [km]')
    a2.legend(loc='best')
    a2.grid(True)

    plotisr(pp, 10,(None,None),ifn)
    plotisr(pp, 11,(90,300),ifn)

def plotisrparam(pp,fgn,zlim,ifn):
    bn = Path(ifn).name
    figure(fgn).clf()

    fg,ax = subplots(nrows=1,ncols=3,sharey=True, num=fgn, figsize=(12,5))
    ax[0].plot(pp['ne'], pp.index)
    ax[0].set_xlabel('$n_e$')
    ax[0].set_ylabel('alt [km]')
    ax[0].set_xscale('log')

    ax[1].plot(pp['vi'], pp.index)
    ax[1].set_xlabel('$v_i$')
    ax[1].set_title(bn,y=1.05)


    ax[2].plot(pp['Ti'], pp.index, label='$T_i$')
    ax[2].plot(pp['Te'], pp.index, label='$T_e$')
    ax[2].set_xlabel('Temperature')
    ax[2].legend(loc='best')

    for a in ax:
        a.set_ylim(zlim)
        a.grid(True)

#    #fg.tight_layout() #no, it spaces the subplots wider
    fg.subplots_adjust(wspace=0.075) #brings subplots horizontally closer

def plotExcrates(spec,tReq=None):
    if spec.ndim==3 and isinstance(tReq,datetime):
        spec = spec.loc[tReq,...]
    elif spec.ndim==3:
        spec = spec[-1,...]
    elif spec.ndim==2:
        pass
    else:
        return

    ax = figure().gca()
    ax.plot(spec.values, spec.alt_km)
    ax.set_xscale('log')
    ax.set_xlim(left=1e-4)
    ax.set_xlabel('Excitation')
    ax.set_ylabel('altitude [km]')
    ax.set_title(f'excitation rates: {spec.name} eV')
    ax.legend(spec.reaction.values)
    ax.grid(True)
