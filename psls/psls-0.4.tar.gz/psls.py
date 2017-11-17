#!/usr/bin/env python

import numpy as np
import math
import matplotlib.pyplot as plt
import sls
import os
import re 
import yaml
import sys
import getopt
import shutil
import transit as tr


'''

PSLS : PLATO Solar-like Light-curve Simulator
(based on SLS,  the Solar-like Light-curve Simulator, see sls.pdf and sls.py)

Copyright (c) October 2017, R. Samadi (LESIA - Observatoire de Paris)

This is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this code.  If not, see <http://www.gnu.org/licenses/>.

'''


__version__ = 0.3

jupiterRadius = 71492.0  # km
ua2Km = 149.59e6  # km
    
def generateZ(orbitalPeriodSecond, planetSemiMajorAxis,
              starRadius, SamplingTime, IntegrationTime, TimeShift, sampleNumber,
              orbitalStartAngleRad, p):
    '''
    :INPUTS:
    orbitalPeriodSecond = orbital period of the planet in second
    planetSemiMajorAxis = semi Major axis in km
    starRadius = star radius in km
    SamplingTime:int = Sampling time in second, (Plato = 25s)
    IntegrationTime : integration time in seconds
    TimeShift: time shift in seconds
    sampleNumber = number of sample we want (==> z.size)
    orbitalStartAngleRad = orbital angle in radians where to start planet position
    :OUTPUTS:
    z = d / r*, is the normalized separation of the centers (sequence of positional offset values)
    
    E. Grolleau
    '''
    angleIncrement = SamplingTime * 2.0 * math.pi / orbitalPeriodSecond 
    angle0 = orbitalStartAngleRad + (IntegrationTime/2. + TimeShift)* 2.0 * math.pi / orbitalPeriodSecond 
    angles = [angleIncrement * sampleIndex +  angle0
              for sampleIndex in range(sampleNumber)]
    # For occultquad computation we need that z < p+1
    z = np.full(shape=(sampleNumber), fill_value=p + 1)
    time = np.arange(sampleNumber) * SamplingTime + IntegrationTime/2. + TimeShift
    i = 0    
    for angle in angles:
        # When angles [pi and 2pi] the planet is behind the star
        if np.sin(angle) > 0:            
            z[i] = abs((planetSemiMajorAxis / starRadius) * np.cos(angle))
            # For occultquad computation we need that z < p+1
            if z[i] >= (p + 1):
                z[i] = p + 1  # max value
        # print i, angle, np.sin(angle), z[i]
        # print z[i]
        i += 1

    return (time, z)
    
def systematics_spectrum(f,parameters,verbose=0):
    """
    f : frequency values [muHz]
    parameters:  (sigma,tau) where  sigma: amplitude (in ppm) and tau: characteristic time (in days)
    A "single-sided power spectrum" is assumed

    """
    sigma= parameters[0] # in ppm
    tau =parameters[1]*86400. # characteristic time, converted from days to seconds
    H = 4.*tau*sigma**2*1e-6
    if(verbose):
        print ("Noise component due to systematics, adopted parameters: sigma = %g [ppm], tau = %f [days], %f [s]") % (sigma,tau/86400.,tau)
    return sls.plf(f,H,tau*1e-6,2.)



def psd (s,dt=1.):
    '''
 Inputs:
 s : signal (regularly sampled)
 dt: sampling (seconds)

 Outputs:
 a tuple (nu,psd)
 nu: frequencies (Hz)
 psd: power spectral density  (in Hz^-1). A double-sided PSD is assumed
    '''
    
    ft=np.fft.fft(s)
    n=len(s)
    ps=(np.abs(ft))**2*(dt/n)
    nu=np.fft.fftfreq(n,d=dt)
    nnu=n/2
    return (nu[0:nnu],ps[0:nnu])




def rebin1d(array,n):
    nr=int(float(array.shape[0])/float(n))
    return (np.reshape(array,(n,nr))).sum(1)
 
def search_model(ModelDir,ES,logg,teff,  dlogg=0.01,dteff=15.,verbose=False,plot=False):
    
    pack = np.load(ModelDir+'data.npz')
    files = pack['files']     
    glob = pack['glob'] # star global parameters
    ## references = pack['references'] # references (&constants) parameters
    
    if(ES.lower() == 'any'):
        sel = np.ones(glob.shape[0],dtype=np.bool)
    elif(ES.lower() == 'ms'):
        sel = (glob[:,28] > 1e-3)
    elif(ES.lower() == 'sg'):
        sel = (glob[:,28] <= 1e-3) & (glob[:,20] < 200.) 
    else:
        raise sls.SLSError("unmanaged evolutionary status:"+ ES)
    
    if(sel.sum()==0):
        raise sls.SLSError("no models full fill the criteria ")
    
    glob = glob[sel,:]
    files = files[sel]
    
    Chi2 = ((glob[:,17]-teff)/dteff)**2 +  ((glob[:,18]-logg)/dlogg)**2
    
    i = np.argmin(Chi2)
    teffb = glob[i,17]
    loggb = glob[i,18]
    name = re.sub('-[n]ad\.osc','',os.path.basename(files[i]))
    
    if(verbose):        
        print ('Best matching, teff = %f ,logg = %f, Chi2 = %f') % (teffb, loggb,Chi2[i])   
        print ('Star model name: %s') % (name)
        
    if(plot):
        plt.figure(200)
        plt.clf()
        plt.plot(glob[:,17],glob[:,18],'k+')
        plt.plot([teffb],[loggb],'ro')
        plt.gca().invert_yaxis()
        plt.gca().invert_xaxis()
        plt.ylabel(r'$log g$')
        plt.xlabel(r'$T_{\rm eff}$ [K]')
        plt.draw()
        
    return   name  , teffb , loggb
    
    '''
    files = pack['files']     
    glob = pack['glob'] # star global parameters
    
    
    glob[i,j],
    i: model index
    j: parameter index:
      0 : M_star
      1 : R_tot
      2 : L_tot
      3 : Z0
      4 : X0
      5 : alpha
      6 : X in CZ
      7 : Y in CZ
      8 : d2p
      9 : d2ro
      10 : age
      11 : wrot initial (global rotation velocity)
      12 : w_rot initial
      13 : g constante de la gravitaion
      14 : msun
      15 : rsun
      16 : lsol
      17 : Teff
      18 : log g
      19 : Tc temperature at the center
      20 : numax (scaling) [muHz]
      21 : deltanu (scaling) [muHz]
      22 : acoustic diameter [sec]
      23 : nuc, cutoff frequency, at the photosphere [muHz]
      24 : nuc, cutoff frequency, at the r=rmax [muHz]
      25 : deltaPI_1 [sec]
      26,27 : r1,r2 -> interval in radii on which the Brunt-Vaisala is integrated for the calculation of deltaPI
      28 : Xc
      29 : Yc
      30 : acoustic diameter [sec], computed on the basis of the .amdl file (can be oversampled)
      31 : acoustic depth of the Gamma1 bump associated with the first He ionization zone
      32 : acoustic depth of the Gamma1 bump associated with the second He ionization zone
      33 : acoustic depth of the base of the convective zone    

    references[i]: some references values:
            0: msun
            1: rsun
            2: lsun
            3: teff sun
            4: logg sun
            5: numax ref. (Mosser et al 2013)
            6: deltanu ref. (Mosser et al 2013)
            7: nuc sun (Jimenez 2006)
    '''


def usage():
    print "usage: psls.py config.yaml"
    print "      : "
    print "Options:"
    print "-v : print program version"
    print "-h : print this help"
    print "-P : do some plots"
    print "-V : verbose mode"
    print "-f : save the LC associated with each camera group, otherwise average over the camera groups (default choice)"
    print "-o <path> : output directory (the working directory is by default assumed)"
    



if(len(sys.argv)<2):
    usage()
    sys.exit(2)
try:
    opts,args = getopt.getopt(sys.argv[1:],"hvPVo:f")

except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

Verbose = False
Plot = False
OutDir = '.'
FullOutput =  False 
 
for o, a in opts:
    if o == "-h" :
        usage()
        sys.exit(1)
    elif o == "-v":
        print __version__
        sys.exit(1)
    elif o == "-V":
        Verbose = True
    elif o == "-P":
        Plot = True
    elif o == "-f":
        FullOutput = True
    elif o == "-o":
        OutDir = a
    else:
        print "unhandled option %s" % (o)
        sys.exit(1)


nargs = len(args)
if nargs > 1 :
    print "too many arguments"
    usage()
    sys.exit()

if nargs < 1 :
    print "missing arguments"
    usage()
    sys.exit()

config=args[0]




stream = file(config, 'r')    # 'document.yaml' contains a single YAML document.
cfg = yaml.load(stream)
stream.close()

OutDir = os.path.normpath(OutDir) + '/'
StarModelDir = cfg['StarModelDir']

StarModelDir = os.path.normpath(StarModelDir) + '/'
StarID = cfg['StarID']
StarName = ("%10.10i") % StarID
StarTeff,StarLogg = cfg['StarTeff'],cfg['StarLogg']
StarES = cfg['StarES']
if(Verbose):
    print 'Star name: ' + StarName
    print ('teff = %f ,logg = %f') % (StarTeff, StarLogg)   
    
UP = (StarES.lower() == 'rg') 

if (UP):
    DPI = cfg['DPI']
    q = cfg['q']
    numax = cfg['numax']
    delta_nu =  cfg['delta_nu']    
else:
        
    StarModelName,StarTeff,StarLogg = search_model(StarModelDir,StarES,StarLogg,StarTeff,verbose=Verbose,plot=Plot)
    StarFreqFile = StarModelDir+StarModelName + '.gsm'
    ## _, (mass, radius) = sls.read_agsm(StarFreqFile)
    ## logg = sls.logg_sun + math.log10(mass) - 2* math.log10(radius)
     
     
    if(Verbose):
        print ('teff = %f ,logg = %f') % (StarTeff, StarLogg)   
        
    
    logTeff = math.log10(StarTeff)
    SurfaceEffects = cfg['SurfaceEffects']
    if(SurfaceEffects):
        # from Sonoi et al 2015, A&A, 583, 112
        logma =  7.69 * logTeff -0.629 * StarLogg -28.5
        logb = -3.86*logTeff  + 0.235 * StarLogg + 14.2
    
        a =  - 10.**logma
        b = 10.**logb
        if(Verbose):
            print ('Surface effects parameters, a = %f ,b = %f') %  (a,b)
    
    else:
        a = 0.
        b = 1.


OutDir = os.path.normpath(OutDir) + '/'
Activity = cfg['Activity']
if(Activity):
    activity = (cfg['ActivitySigma'],cfg['ActivityTau'])
else:
    activity = None

Transit = cfg['Transit']

IntegrationTime = cfg['IntegrationTime']

# initialization of the state of the RNG
MasterSeed = cfg['MasterSeed']
NGroup = cfg['NGroup']

np.random.seed(MasterSeed)
seeds = np.random.randint(0, 1073741824 + 1,size=NGroup+1)
Sampling,Duration,StarMag = cfg['Sampling'],cfg['Duration'],cfg['StarMag']

if (UP):
    # Simulated stellar signal, noise free, UP
    time,ts,f,ps,mps_nf,opar,_ =  sls.gen_up(StarID, numax,Sampling,Duration, StarMag,delta_nu =  delta_nu, mass = -1. , seed =seeds[0] , pn_ref = 0.,  wn_ref= 0., mag_ref = 6.,verbose = Verbose, teff = StarTeff, DPI = DPI,  q = q , GST = 1 , incl = cfg['Inclination'] , rot_f = cfg['CoreRotationFreq'] )

else:
    # Simulated stellar signal, noise free
    time,ts,f,ps,mps_nf,opar,_ = sls.gen_adipls(StarID,StarFreqFile,StarTeff,Sampling,Duration,StarMag,verbose=Verbose,seed=seeds[0],
                                            mag_ref=StarMag,pn_ref= 0.,wn_ref= 0., a=a,b=b,plot=0, rot_period_sur =  cfg['SurfaceRotationPeriod'] , 
                                            incl = cfg['Inclination'] , activity = activity, granulation=cfg['Granulation'])


if(Transit):
    SampleNumber = time.size
    StarRadius = opar[0]['radius']*sls.rsun*1e-5 # in km
    PlanetRadius = cfg['PlanetRadius'] * jupiterRadius  # in km
    p = PlanetRadius / StarRadius
    _, z = generateZ(cfg['OrbitalPeriod']*86400., cfg['PlanetSemiMajorAxis']*ua2Km,
              StarRadius,Sampling, IntegrationTime, 0. , SampleNumber,
              cfg['OrbitalStartAngle']*math.pi/180., p)
    gamma = [.25, .75]
    transit = tr.occultquad(z, p, gamma, verbose=Verbose)
    if(Verbose):
        print ('Star radius [solar unit]: %f') % ( opar[0]['radius']) 
        print "Planet Radius/ Star Radius = {0:}".format(p)
        print ("Transit depth: %e" ) % (np.max(transit)/np.min(transit)-1.)
    if(Plot):
        plt.figure(110)
        plt.clf()
        plt.title(StarName+ ', transit')
        plt.plot(time/86400.,(transit-1.)*100.)
        plt.ylabel('Flux variation [%]')
        plt.xlabel('Time [days]')
        plt.draw()

    
# Total white-noise level ppm/Hz^(1/2), for a each single Camera 
NSR = cfg['NSR']
W =  NSR*math.sqrt(3600.) #  ppm/Hz^(1/2)
SystematicsWhite = cfg['SystematicsWhite']
SW = SystematicsWhite*math.sqrt(3600.)

opar[1]['white_noise'] = W #  ppm/Hz^(1/2)
dt = opar[1]['sampling'] 
nyq = opar[1]['nyquist']
if(Verbose):
        print 'Total white-noise for one Camera [ppm/Hz^(1/2)]:',W
        print 'Total white-noise at sampling time:',W*math.sqrt(1./dt)
        print 'Nyquist frequency [muHz]',nyq


Systematics = (cfg['SystematicsSigma'],cfg['SystematicsTau'])
SC  = systematics_spectrum(f,Systematics,verbose=Verbose) # Systematic components
SCf = systematics_spectrum(2.*nyq-f,Systematics) # Folded component  
        
# mean power spectrum associated with  non-stellar noise only (random + systematics) [ppm2/Hz]
# warning; single-sided PSD is assumed by sls.mpsd2rts()
mps_N =  (  SC + SCf ) *   (np.sinc(0.5*f/nyq))**2  + 2.* SW**2*1e-6 +  2.*W**2  * 1e-6 # [ppm^2/muHz] 

nt = time.size
full_ts = np.zeros((nt,NGroup,3))
nu = np.fft.fftfreq(nt,d=dt)[0:nt/2] * 1e6 # frequencies, muHz
nnu = nu.size
spec = np.zeros((NGroup,nu.size))
dnu = nu[1]
TimeShift = cfg['TimeShift']
NCamera = cfg['NCamera']

for i in range(NGroup):
    time_i, ts_i , ps_i, _ =  sls.mpsd2rts(f*1e-6,mps_nf*1e6,seed=seeds[0],time_shift=i*TimeShift)
    full_ts[:,i,0,] = time_i +  IntegrationTime/2.
    _, ts_N_i , ps_N_i, _ =  sls.mpsd2rts(f*1e-6,mps_N*1e6,seed=seeds[i+1])
    ts = (1. + ts_i*1e-6) * (1. + ts_N_i*1e-6/math.sqrt(NCamera))
    if(Transit):
        p = PlanetRadius / StarRadius
        _, z = generateZ(cfg['OrbitalPeriod']*86400., cfg['PlanetSemiMajorAxis']*ua2Km,
                         StarRadius,Sampling, IntegrationTime, i*TimeShift , SampleNumber,
              cfg['OrbitalStartAngle']*math.pi/180.,p )
        gamma = [.25, .75]
        ts *= tr.occultquad(z, p, gamma, verbose=Verbose)
    
    # relative flux variation, in ppm
    ts = (ts/np.mean(ts) - 1.)*1e6
    full_ts[:,i,1] = ts
    full_ts[:,i,2] = i+1


# LC averaged over the camera groups  
single_ts = np.sum(full_ts,axis=1)/float(NGroup)
single_ts = single_ts [:,0:2]
single_nu,single_psd  = psd(single_ts[:,1],dt=dt)
single_nu *= 1e6 
single_psd *= 1e-6 # [ppm^2/muHz] 
   

if(Plot):   
    plt.figure(100)
    plt.clf()
    plt.title(StarName+', PSD')
    

    plt.plot(single_nu[1:],single_psd[1:],'grey',label='simulated (raw)')
    if (UP):
        win = 0.1
    else:
        win  = 10. # muH
    m = int(round(win/single_nu[1]))
    p = nnu/m
    
    num = rebin1d(single_nu[0:p*m],p)/float(m)
    psdm = rebin1d(single_psd[0:p*m],p)/float(m)
    psdme = 0.5*(mps_nf[1:]+mps_N[1:]/(NCamera*NGroup)) # mean expected PSD for all camera 
    plt.plot(num[1:],psdm[1:],'k',lw=2,label='simulated (mean)') # simulated spectrum, all camera

    # factor 1/2 to convert  the PSD from single-sided to double-sided PSD
    ## plt.plot(f[1:], 0.5*(mps_nf[1:]+mps_N[1:]),'g',lw=2,label='one camera') # single camera
    plt.plot(f[1:], psdme ,'b',lw=2,label='star+instrument')  # All Camera
    plt.plot(f[1:], 0.5*mps_nf[1:],'r',lw=2,label='star') # noise free
    plt.plot(f[1:], 0.5*( (mps_N[1:]  - 2*W**2*1e-6) /(NCamera*NGroup)),'m',lw=2,label='systematics') # all Camera
    plt.plot(f[1:], 0.5*(mps_N[1:]/(NCamera*NGroup)),'g',lw=2,label='instrument') # all Camera


    plt.loglog()
    plt.xlabel(r'$\nu$ [$\mu$Hz]')  
    plt.ylabel(r'[ppm$^2$/$\mu$Hz]')
    plt.axis(ymin=psdme[-1]/100.)
    plt.legend(loc=1)
    fname = OutDir + StarName+ '_fig1.png'
    plt.savefig(fname)

    plt.figure(101)
    plt.clf()
    plt.title(StarName)
    numax =  opar[2]['numax']
    Hmax = opar[2]['Hmax']  
    u =     (num> numax*0.5) & (num < numax*1.5)
    plt.plot(num[u],psdm[u],'k',lw=2) # simulated spectrum, all camera

    
    plt.loglog()
    plt.xlabel(r'$\nu$ [$\mu$Hz]')  
    plt.ylabel(r'[ppm$^2$/$\mu$Hz]')    


    plt.figure(102)
    plt.clf()
    plt.title(StarName)
    plt.plot(num[u],psdm[u],'k',lw=2) # simulated spectrum, all camera
    plt.xlabel(r'$\nu$ [$\mu$Hz]')  
    plt.ylabel(r'[ppm$^2$/$\mu$Hz]')    


    plt.figure(103)
    plt.clf()
    plt.title(StarName)
    u =     (f> numax*0.5) & (f < numax*1.5)
    plt.plot(f[u], 0.5*mps_nf[u],'r',lw=2,label='star') # noise free
    plt.xlabel(r'$\nu$ [$\mu$Hz]')  
    plt.ylabel(r'[ppm$^2$/$\mu$Hz]')    

    m = int( round(3600./Sampling))
    p = time.size/m
    tsm = rebin1d(single_ts[0:p*m,1],p)/float(m)
    timem = rebin1d(time[0:p*m],p)/float(m)

    plt.figure(104)
    plt.clf()
    plt.title(StarName+', light-curve')
    plt.plot(time/86400.,single_ts[:,1]*1e-4,'grey')
    plt.plot(timem/86400.,tsm*1e-4,'k')
    plt.xlabel('Time [days]')  
    plt.ylabel('Flux variation [%]')
    fname = OutDir + StarName+ '_fig4.png'
    plt.savefig(fname)
    

fname = OutDir + StarName+ '.dat'
if(Verbose):
    print 'saving the simulated light-curve as: ',fname

def ppar(par):
    n = len(par)
    i = 0 
    s = ''
    for u in par.items():
        s += ' %s = %g' % u
        if (i < n-1):
            s += ', '
        i += 1
    return s

hd = ''
hd += ('StarID = %10.10i\n') % (StarID)  
hd += ("Master_seed = %i\n") % (MasterSeed)
hd += ("Version = %7.2f\n") % (__version__)


if(FullOutput):
    full_ts = full_ts.reshape((nt*NGroup,3))  
    np.savetxt(fname,full_ts,fmt='%12.2f %20.15e %1i',header=hd + '\nTime [s], Flux variation [ppm], Group ID')
else:
    np.savetxt(fname,single_ts,fmt='%12.2f %20.15e',header=hd + '\nTime [s], Flux variation [ppm]')

hd += '# star parameters:\n'
hd += (' teff = %f ,logg = %f\n') % (StarTeff, StarLogg)  
hd += ppar(opar[0])
hd += '\n# observations parameters:\n'
hd += ppar(opar[1])
hd += '\n# oscillation parameters:\n'
hd += ppar(opar[2])
hd += '\n# granulation parameters:\n'
hd += ppar(opar[3])
hd += '\n# activity parameters:\n'
hd += ppar(opar[4])

fname = OutDir + StarName+ '.txt'
f = open(fname,'w')
f.write(hd)
f.close()
fname = OutDir + StarName+ '.yaml'
shutil.copy2(config,fname)

if(Verbose):
    print 'done'
    
    
if(Plot):
    plt.draw()
    plt.show(block=False)
    
if(Verbose):
    s=raw_input('type ENTER to finish')



