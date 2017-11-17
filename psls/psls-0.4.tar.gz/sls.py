import numpy as np
import math
import matplotlib.pyplot as plt
import re
import scipy.optimize
import FortranIO
import universal_pattern as UP

''''

Solar-like Light-curve Simulator (SLS)

Simulate stochastically-excited oscillations and associated stellar background (granulation and activity).

Two different types of oscillation spectrum can be simulated:
- gen_up : oscillation spectrum based on the Universal Pattern  by Mosser et al (2011, A&A, 525, L9).
   Mixed-modes can been included when the asymptotic period spacing is specified.

- gen_adipls: oscillation spectrum based on eigenfrequencies computed with ADIPLS 

For more details see the helps associated with the procedures gen_up() and gen_adipls()

Other procedures are:

- genslc():  from an individual simulation, generate a series of simuated ligth-curves and save them in a set of files (one per light-curve). Each simulated light curve corresponds to a given realization. 

- savelc() : save a given light-curve in a ASCII file

- test_gen_up() : perform a simple illustrative test assuming the Universal Pattern (call to  gen_up)

- test_gen_adipls() : perform a simple illustrative test  using a set of eigenfrequencies computed with ADIPLS  (call to gen_adipls)



Copyright (c) 2014, Reza Samadi, LESIA - Observatoire de Paris

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

# numax reference value (Mosser et al 2013, SF2A)
numaxref= 3104.

# solar constants
nucsun = 5300.  # sun cutt-off freq.
numaxsun = 3100.
deltanusun = 135.
teffsun = 5777.
msun = 1.98919e33           # solar mass
rsun = 6.9599e10            # solar radius
gmsun = 1.32712438e26       # G Msun
logg_sun = math.log10(gmsun) - 2.*math.log10(rsun)
ggrav = gmsun/msun          # grav. constant G

	
class SLSError(Exception):
	def __init__(self, value):
         	self.value = value
	def __str__(self):
		return repr(self.value) 

def rebin1d(array,n):
	nr=int(float(array.shape[0])/float(n))
	return (np.reshape(array,(n,nr))).sum(1)

def gaussenvelop(nu,A,nu0,width):
	'''
	Gassian envelop for the oscillation spectrum

	INPUTS
	nu: frequencies
	A: amplitude of the envelope
	nu0: position in frequency (numax)
	width: width of the envelope
	
	'''
        return A*np.exp(-((nu-nu0)**2)/(width**2/(4*math.log(2)))) 
        
def plf(nu,h,tau,alpha):
	'''
	Pseudo Lorentzian Function (plf) for the granulation component(s)

	INPUTS:
	nu:  frequencies
	h: height
	tau : characteristic time
	alpha : slope
	
	'''

	return h/(1. + (2.*math.pi*tau *nu)**alpha)

def eft_2plf(h1,tau1,alpha1,h2,tau2,alpha2):
    # Given two pseudo lorenztian functions (plf), compute the associated e-folding time (eft)
    N = 2l**19
    Nf = N/2  + 1
    tau = min(tau1,tau2)
    sampling =  tau*1e-3
    dnu = 1./(sampling*N)
    nu = np.arange(Nf) * dnu

    spc = plf(nu,h1,tau1,alpha1) + plf(nu,h2,tau2,alpha2)
    acf = np.fft.irfft(spc,n=N)
    acf = acf[1:N/2]/acf[0]
    time = (np.arange(N/2-1)+1.)*sampling/tau
    eft = np.interp(math.exp(-1),acf[::-1],time[::-1])*tau

    return eft

def mpsd2rts(f,mpsd,seed=None,time_shift=0.):
    '''

    Simulate a random time-series from a mean power spectral density spectrum

    time, ts, ps, seed =  mpsd2rts(f,mpsd,seed=None)

    INPUTS:
    f: frequencies (Hz)
    mpsd : mean power spectral density (PSD) in /Hz. Single-sided PSD
    seed: seed of the Random Number Generator (RNG)
    time_shift : imposes a time shift (seconds), default: 0.

    OUTPUTS:
    time: time values
    ts: simulated time-series
    ps: simulated power spectrum [/Hz]
    seed:  adopted value of the seed (chosen by the Random Number Generator if seed is not specified in input)
    
    '''

    # dnu: frequency resolution in Hz
    if (f[0] ==0. ):
        dnu = f[1]
        n = f.size
        i0 = 0
    else:
        dnu = f[0]
        n = f.size + 1
        i0 = 1

    # sampling time [s]
    dt = 1./(2.*dnu*n)

    # 
    time = np.arange(2*n) * dt  + time_shift

    if( seed == None):
	    # see is not specified, we choose a random value 
	    seed = np.random.random_integers(0,high=2**30)    
    # initialization of the state of the RNG
    np.random.seed(seed)
	
    
    # real and imaginary part randomly distributed
    Rr = np.random.normal(loc=0.,scale=1./math.sqrt(2.),size=n-i0)
    Ri = np.random.normal(loc=0.,scale=1./math.sqrt(2.),size=n-i0)

    # fourier spectrum
    tf = np.zeros(n,dtype=np.complex)
    
    tf[i0:] = np.sqrt(mpsd) * (Rr + Ri*1j)  * np.sqrt(n/dt)
    if(time_shift !=0):
        fp = np.arange(n)*dnu # frequencies, Hz
        tf[i0:] *= np.exp(2.*math.pi*fp[i0:]*time_shift*1j)

    # symmetrise
    tf = np.hstack((
                    np.array([0]),
                    tf[1:],
                    np.array([0]),
                    tf[:0:-1].conj()))        


    # generate the time series [ppm]
    ts = np.real(np.fft.ifft(tf)) 

    # power spectrum in /Hz
    ps = np.abs(tf[i0:n])**2 *(dt/n)

    return time,ts,ps,seed

def power_ratio(l,beta):
    '''

    power_ratio (l,i)

    Returns the mode relative power amplitude for a given angle i with respect to the mode power amplitude at the angle i=0, 
    i.e. returns the quantity given by (see eg. Dziembowski, 1971, Toutain & Goutterbroze 1993) :
    Q^2_lm = (l-m)!/(l+m)! ( P_lm[cos(i)] )^2
    where i is the inclination angle (i=0 corresponds to the direction of the rotation axis, ie. theta=0).  
        
    INPUTS:
    l: mode angular degree
    i: inclination angle in degree (i=0 points toward the observer)
    
    '''

    def combi (n,r):
        '''
        Compute combinations n r,  for  n>r

        '''
        c = math.factorial(n)/math.factorial(n-r)/math.factorial(r)
        return c



    def dmm(l,m1,m2,beta):
        '''

        compute dm1,m2(beta)  for  m1+m2>=0  and m1-m2>=0

        '''
        co = math.cos(beta/2.)
        si = math.sin(beta/2.)

        sum=0.
        for s in range(0,l-m1+1):
            var=0.
            var=combi(l+m2,l-m1-s)*combi(l-m2,s)*(-1.)**(l-m1-s)
            var=var*co**(2*s+m1+m2)*si**(2*l-2*s-m1-m2)
            sum=sum+var

        sum=sum*math.sqrt(math.factorial(l+m1)*math.factorial(l-m1)*1.)
        sum=sum/math.sqrt(math.factorial(l+m2)*math.factorial(l-m2)*1.)

        return sum


    def function_rot(l,beta):

        dim = 2*l+1
        mat = np.zeros((dim,dim))
        for i in range(0,l+1):
            for j in range(-i,i+1):
                  mat[i+l,j+l] = dmm(l,i,j,beta)

        for i in range(-l,1):
              for j in range(i,-i+1):
                  mat[i+l,j+l] = mat[-i+l,-j+l]*(-1.)**(i-j)

        for j in range(0,l+1):
            for i in range(-j,j+1):
                  mat [i+l,j+l] = dmm(l,j,i,-beta)

        for j in range(-l,1):
            for i in range(j,-j+1):
                  mat [i+l,j+l] = mat[-i+l,-j+l]*(-1.)**(i-j)

        return mat

    angle = math.pi*beta/180.
    zz = function_rot(l,angle)
    zz = zz[:,l]**2
    norm = zz.sum()
    return zz/norm

def activity_spectrum(f,parameters,verbose=0):
    """
    f : frequency values [muHz]
    parameters:  (sigma,tau) where  sigma: amplitude (in ppm) and tau: characteristic time (in days)
    An "single-sided power spectrum" is assumed

    """
    sigma= parameters[0] # in ppm
    tau =parameters[1]*86400. # characteristic time, converted from days to seconds
    H = 4.*tau*sigma**2*1e-6
    if(verbose):
        print ("activity parameters: sigma=%f [ppm], tau= %f [days] %f [s]") % (sigma,tau/86400.,tau)
    return plf(f,H,tau*1e-6,2.)

def granulation_spectrum(f,numax,verbose=0,type=0,mass=1.):
    
    '''
   Granulation spectrum
   
   GS,parameters = granulation_spectrum(numax,tau)
   We assume an "single-sided power spectrum"

   INPUTS:
   f : frequency values [muHz]
   numax: peak frequency [muHz]
   type :
   =0 -> assume standard scaling relations and a Lorentzian form
   =1 -> as in Kallinger et al (2014)
   mass : star mass (used for type=1)
   
   OUTPUTS:
   GS: the granulation spectrum computed for the frequency set f
   parameters: granulation parameters, the returned parameters depend on "type"

   type = 0 : parameters = (H,tau,sigma)
      H: Height of the granulation component [ppm2/muHz]
      tau: time-scale [s]
      sigma: amplitude of the granulation [ppm]

   type = 1 : parameters = (h1,tau1,c1,h2,tau2,c2)
   
    '''
    if (type==0):
	    
        tau_gran =  9e4*(numax/10.)**(-0.90) # time scale [seconds]  ref. M13
        taue = tau_gran # e-folding type, taue = tau_gran for a Lorentzian function
	    #    h_gran =  2e6*(tau_gran/1e5) **2.34 # height [ppm2/muHz]  ref.  M13
        h_gran = 4e5*(numax/10.)**(-2.15) # height [ppm2/muHz]  ref.  M13
        sigma_gran =  math.sqrt(h_gran*1e6/tau_gran/4.)
        if(verbose):
		    print ("tau [s], H [ppm2/muHz], sigma [ppm]: %e, %e, %f, %g")%   (h_gran , tau_gran , sigma_gran,taue)
	gran_par = {"h1": h_gran, "tau1": tau_gran, "alpha1": 2.,"taue": taue}
        return plf(f,h_gran,tau_gran*1e-6,2.), gran_par
    else:
	    if ( (numax < 2.) | (numax > 3500.)):
		    raise SLSError("Outside the valid numax domain of Kallinger et al (2014) scaling relations for the granulation spectrum")
	    a1k = 3382
	    a1s = -0.609
	    a1t = 0.

	    a2k = 3710.
	    a2s = -0.613
	    a2t = -0.26

	    b1k = 0.317
	    b1s = 0.970

	    b2k = 0.948
	    b2s = 0.992

	    c1 = 4.
	    c2 = 4.

	    a1 = a1k*numax**a1s*mass**a1t
	    a2 = a2k*numax**a2s*mass**a2t

	    b1 = b1k*numax**b1s
	    b2 = b2k*numax**b2s


	    xi1 = 2.*math.sqrt(2.)/math.pi
	    tau1   = 1./(2.*math.pi)/b1

	    xi2 = xi1
	    tau2   = 1./(2.*math.pi)/b2

            h1 = a1**2/b1*xi1
            h2 = a2**2/b2*xi2
            taue = eft_2plf(h1,tau1,c1,h2,tau2,c2) # e-folding time
	    gran_par = {"h1": h1, "tau1": tau1, "alpha1": c1,"h2": h2, "tau2": tau2, "alpha2": c2,"taue": taue}
            if(verbose):
             	print ("h1 [ppm2/muHz], tau1 [s], c1, h2 , tau2 , c2: %g, %g, %g, %g, %g, %g, %g") % (h1,tau1*1e6,c1,h2,tau2*1e6,c2,taue)

            return  plf(f,h1,tau1,c1) + plf(f,h2,tau2,c2),gran_par

def amax(numax,deltanu,teff):
    '''

    Scaling relation for the oscillation maximum (Amax) as established by Corsaro et al (2013, MNRAS 430, 2313-2326)

    We assume the model named  4\beta (see Table 3 & 4)
    
    If numax >150 muHz,  coefficients established using the short cadence data (table 3) are assumed otherwise those obtained with the long cadence data (table 4).
    
    
    Return the value of Amax bolometric (ppm) as a function of numax (muHz), deltanu (muHz) and teff (K)
    

    '''

    if ( (numax > 4000.) | (numax < 2.) ):
	    raise SLSError("numax outside the domain for the oscillation maximum scaling relation of  Corsaro et al (2013)")


    Amaxbolsun = 2.53 # rms value (see Michel et al 2009)

    if( numax > 150.):
	    # parameters of model 4\beta for short cadence data
	    s = 0.748
	    r = 3.47
	    t = 1.27
	    lnbeta = 0.321

        ## model M1 
        ## s = 0.624
        ## r = 3.68
        ## lnAmax = -s*math.log(numax/numaxsun) + (3.5*s -r + 1.) *math.log(deltanu/deltanusun)
        ## Amaxbol = math.exp(lnAmax) * (teff/5934.)**(0.8) *Amaxbolsun
    else:
	    # parameters of model 4\beta for long cadence data
	    s = 0.602
	    r = 5.87
	    t = 1.32
	    lnbeta = 0.45

    lnAmaxbol = (2.*s-3.*t)*math.log(numax/numaxsun) + (4.*t-4.*s)*math.log(deltanu/deltanusun) + (5.*s-1.5*t-r+0.2)*math.log(teff/teffsun) + lnbeta

    Amaxbol = math.exp(lnAmaxbol)*Amaxbolsun

    return Amaxbol


def lwmax(teff):
    '''
    Scaling relation for the mode linewidth at numax as established by Appourchaux et al (2012, A&A, 537, A134)

    Return the mode linewidth (muHz) at numax as a function of teff (K)
    
    '''
    if ( (teff > 6700.) | (teff < 5300.) ):
	    raise SLSError("Teff outside the domain for the mode line-width scaling relation of Appourchaux et al (2012)")
    # Appourchaux et al (2012), table 2, at maximum mode height
    Gamma0 = 0.20
    alpha = 0.97
    s = 13.0


    return  Gamma0 + alpha*(teff/teffsun)**s

def get_obs_par(mag, T, dt , pn_ref = 7.7, mag_ref = 6.,wn_ref = 0. , verbose = False, teff = 4800.):
	

    # total white-noise level ppm.s^(1/2)
    W = math.sqrt ( pn_ref**2 * 3600.*10.**((mag-mag_ref)/2.5)  + wn_ref**2    * 3600.*10.**(2.*(mag-mag_ref)/2.5) )
    if(verbose):
        print 'Total white-noise [ppm.Hz^(-1/2)]:',W
        print 'Total white-noise at sampling time:',W*math.sqrt(1./dt)
 ## 2.*W**2*1e-6

    T0 = T*86400. # duration in seconds
    
    # size of the time series
    n = long(T0/(dt))

    # frequency resolution [muHz]
    dnu = 1./(n*dt)*1e6


    nyq = 1./(2.*dt)*1e6 # Nyquist frequency [muHz]

    m2b = (teff/5934.)**(0.8) # conversion from  measured to bolometric amplitude (Ballot et al 2011)

    # observation parameters
    obs_par = {'magnitude': mag, 'duration': T, 'sampling': dt, 'frequency_resolution': dnu, 'nyquist': nyq, 'white_noise': W, 'time_steps_number': n , 'bolometric_coefficient': m2b}
    
    return obs_par


def read_agsm(file):
    '''
     modes,starpar = read_agsm(file)

    
     OUTPUTS:
     modes : mode parameters:
     
     modes[:,0] : n order
     modes[:,1] : l degree
     modes[:,2] : nu frequency in muHz (eigenvalue)
     modes[:,3] : square normalised frequency (w2)
     modes[:,4] : Richardson frequency in muHz
     modes[:,5] : variationnal frequency in muHz
     modes[:,6] : icase
     modes[:,7] : mode inertia g cm^2  x 10^40
     modes[:,8] : Ledoux coefficient

     starpar : star parameters (mass,radius)
     
     
    '''

    f = FortranIO.FortranBinaryFile(file, mode='r')

    cs = []
    while True:
        try:
            csi = f.readRecordNative('d')
            cs.append(csi)
        except IndexError:
            break

    nmodes = len(cs)
    modes = np.zeros((nmodes,9))
    mstar = (cs[0])[1]
    rstar = (cs[0])[2]
    for i in range(nmodes):
        modes[i,0] = (cs[i]) [18] # n
        modes[i,1] = (cs[i]) [17] # l        
        sigma2 = (cs[i]) [19]
        omega2 = sigma2*ggrav*mstar/(rstar**3)
        modes[i,2] = math.sqrt(omega2)/(2.*math.pi)*1e6 # nu in muHz
        modes[i,3] = sigma2
        modes[i,4] = (cs[i]) [36]*1e3 # Richardson frequency in muHz
        modes[i,5] = (cs[i]) [26]*1e3 # variational frequency in muHz
	modes[i,7] = (cs[i]) [23] * (mstar*1e-20) * ( (cs[i])[29 ] *  rstar*1e-10  )**2 *  4. *math.pi 
	modes[i,8]  = (cs[i]) [35] 
	
    f.close()
    # reading separately the 'ics' integer variables
    f = FortranIO.FortranBinaryFile(file, mode='r')
    n = 38*2
    for i in range(nmodes):
        data = f.readRecordNative('i')
        ics = data[n:n+8]
        modes[i,6] = ics[4]

    f.close()

    return modes,(mstar/msun,rstar/rsun)

def osc_spectrum(starID, f,modes,numax,deltanu,teff,verbose=False,a=0.,b=1.,plot=False,win=0, rot_period_sur = -1., incl = 0.):
	# a,b  surface effect parameters (Lorentzian function)
    # rot_period_sur : period of the surface rotation, in days. Do not include splittings if rot_period_sur  < 0

    starName = ("%10.10i") % starID
    Gamma =lwmax(teff)
    Amax = amax(numax,deltanu,teff)
    Hmax = 2.*Amax**2/(math.pi*Gamma) # Mode height at numax assuming resolved modes (from Lochard et al 2005, A&A, 438, 939, eq. 16)
    # the additional factor comes from the fact that Lochard et al 2005 assumed two-side power density spectrum
    # here we assume an single-sided power density spectrum
    nm = modes.shape[0]
    width = 0.66*(numax**0.88)		# dnu_env = FWHM of the excess power envelope, see: Mosser et al. (2012 A&A 537 A30) - Table 2

    if(verbose):
        print '------------------------------------------------------------------------'
        print 'Amax=',Amax,' [ppm]'
        print 'Gamma=',Gamma, ' [muHz]'
        print 'Hmax=',Hmax,' [ppm^2/muHz]'
        print 'Width=',Hmax,' [muHz]'
        print 'theoretical input frequencies:'
        print "n, l, nu_eig, nu_var , nu_eig-nu_var,nu_eig-nu_richardson"
        u = modes[:,6] == 10010
        for i in range(nm):
            if (u[i]):
                print ("%i %i %f %f %f %f") % (modes[i,0],modes[i,1],modes[i,2],modes[i,5],modes[i,2]-modes[i,5],modes[i,2]-modes[i,4])
        print '------------------------------------------------------------------------'
    spec = np.zeros(len(f))
    df = f[1] - f[0]
    # square visibility
    V1 = 1.5
    V2 = 0.5
    V3 = 0.05
    # 
    V = (1.,V1,V2,V3)

### !!! A ADAPTER POUR LES MS !!!

    # identification of the radial modes 
    ir = ( modes[:,1] ==0)
    nr = ir.sum()
    Imax = np.interp(numax,modes[ir,2],modes[ir,7])
    NU = []
    L = [] # angular degrees
    LM = []  # azimuth degree
    N = []
    G = []
    H = []
    I = []
    DNU = [] 
    gauss = lambda nu : np.exp(-((nu-numax)**2)/((2.*width)**2/(4*math.log(2))))
    A = 1.
    fout = open(starName +  '.modes','w')
    fout.write("n, l, m , nu, gamma, h, I/Imax, dnu, splitting\n")

    for i in range(nm): # loop over the modes (n,l)
	inertia = modes[i,7]
	nu0 = modes[i,4] #  Richardson frequency i
	n = int(modes[i,0])
	ell = int(modes[i,1])
        if (rot_period_sur > 0):
        	nlm = 2*ell + 1 # total numver of the multiplets 
            	lm1 = -ell
            	lm2 = ell
 	else:
            	nlm = 1
            	lm1 = 0
            	lm2 = 0
        if (rot_period_sur <= 0.): 
		pr = np.ones(nlm)
	else:
		pr = power_ratio(ell,incl)   
        for lm in range(lm1,lm2+1): # loop over the multiplets 
	    if (rot_period_sur <= 0.):
            	split = 0.	
	    else:
		split = lm/(rot_period_sur*86400.)*1e6*modes[i,8]
##		print lm,modes[i,8]
            icase = int(modes[i,6])
    ##	    dnu = a*numax*(nu/numax)**b # Kjeldsen & Bedding 2008
    ##	    dnu = numax * (c + a/(1. + (nu/numax)**b) )
	    nu = nu0 + split
            dnu = a* numax * (1. -  1./(1. + (nu/numax)**b) ) # surface effects, Eq. 9, Sonoi et al 2015, A&A, 583, 112
            nu = nu + dnu  # we add surface effects
            h = gaussenvelop(nu,Hmax,numax,width)*V[ell]*pr[lm-lm1]
##            gamma = Gamma*(Imax/inertia)* (A - (A-1.)*gauss(nu))
            gamma = Gamma*(Imax/inertia)* (1. + A  - A*gauss(nu))
            if (icase != 10010):
##                if(verbose):
##                    print 'excluded mode according to icase=',icase
                continue
            if (n  <= 0):
##                if(verbose):
##                    print 'excluded mode because n<=0 : ',n
                continue
            if (ell  > 3):
##                if(verbose):
##                    print 'excluded mode because l>3 : ',ell
                continue
            if (verbose):
                fout.write( ("%i %i %i %f %e %e %e %f %f\n") % (n,ell,lm,nu,gamma,h,inertia/Imax,dnu,split))
            if ( gamma > df*2.): # resolved profile
                P =  1./ ( 1. + ( 2.*(f-nu)/gamma)**2 )   # Lorentzian : modes shape
            else: # un-resolved profile
                P = (math.pi*gamma/2./df)*( np.sinc( math.pi*(f-nu)/df) )**2
            spec[:] = spec[:] + P * h
            NU.append(nu)
            L.append(ell)
            LM.append(lm)
            N.append(n)
            G.append(gamma)
            H.append(h)
            I.append(inertia/Imax)
            DNU.append(dnu)
	    
    N = np.array(N)
    L = np.array(L)
    NU = np.array(NU)
    G = np.array(G)
    H = np.array(H)
    I = np.array(I)
    DNU =  np.array(DNU)
    if(plot):
	    plt.close('all')
	    plt.figure(win)
	    plt.clf()
	    plt.plot(NU,G*I,'ro')
	    plt.xlabel(r'$\nu$ [$\mu$Hz]')
	    plt.ylabel(r'$\Gamma (I/I_{\rm max})$ [$\mu$Hz]')
	    plt.semilogy()
	    plt.title(starName)
            plt.savefig(starName +  ("_%2.2i.pdf") % (win) )

            win += 1
	    plt.figure(win)
	    plt.clf()
	    plt.plot(NU,G,'ro')
	    plt.xlabel(r'$\nu$ [$\mu$Hz]')
	    plt.ylabel(r'$\Gamma$ [$\mu$Hz]')
	    plt.semilogy()
            plt.title(starName)
            plt.savefig(starName +  ("_%2.2i.pdf") % (win) )

            win += 1
	    plt.figure(win)
	    plt.clf()
	    plt.plot(NU,I,'ro')
	    plt.xlabel(r'$\nu$ [$\mu$Hz]')
	    plt.ylabel(r'$I/I_{\rm max}$')
	    plt.semilogy()
            plt.title(starName)
            plt.savefig(starName +  ("_%2.2i.pdf") % (win) )

            win += 1
	    plt.figure(win)
	    plt.clf()
	    plt.plot(NU,H,'ro')
	    plt.xlabel(r'$\nu$ [$\mu$Hz]')
	    plt.ylabel(r'$H$ [ppm$^2/\mu$Hz] ')
	    plt.semilogy()
            plt.title(starName)
            plt.savefig(starName +  ("_%2.2i.pdf") % (win) )

            win += 1
	    plt.figure(win)
	    plt.clf()
	    plt.plot(NU,DNU,'ro')
	    plt.xlabel(r'$\nu$ [$\mu$Hz]')
	    plt.ylabel(r'$\delta \nu$ [$\mu$Hz]')
            plt.title(starName)
            plt.savefig(starName +  ("_%2.2i.pdf") % (win) )
    
	    plt.show(block=False)
	    ## s=raw_input('Type ENTER to continue')
    return spec,(Amax,Hmax,Gamma,width),(N,L,LM,NU,G,H,I,DNU)

def gen_adipls(starID, filename, teff, dt,T, mag , seed = None, pn_ref = 7.7, wn_ref = 0. , mag_ref = 6.,verbose = False, GST = 1 , a=0 , b=1.  ,  plot=False, rot_period_sur = -1., incl = 0., activity = None, granulation = True):
    '''

    (time,lc,nu,pds,mpds,par,seed) = gen_adipls( starID, filename, teff, dt,T, mag , seed = None, pn_ref = 7.7, wn_ref = 0. , mag_ref = 6., verbose = False, GST = 1 , a=0 , b=1.  ,  plot=False) 
    
    Generate a simulated light-curve using eigenfrencies computed with ADIPLS

    INPUTS:

    starID : any number to identify the simulation, this is used only for the plots and the generated output files 
    filename: name of the grand summary file (.gsm) generated by ADIPLS
    teff: effective temperature [K]
    dt: sampling time [s]
    T: simulation duration [days]
    mag: magnitude of the star
    seed: seed of the Random Number Generator
    pn_ref: reference value of the photon noise [in ppm per hour]
    wn_ref: reference value of the non-photonic white noise  [in ppm per hour]
    mag_ref: reference magnitude for which pn_ref and wn_ref are specified

    GST: type of granulation spectrum (see the function named 'granulation_spectrum')
    a,b,c: coefficients involved in the formulation used of the surface correction
    plot: if True  do some plot
    verbose: if True be verbose
    rot_period_sur : period of the surface rotation, in days. Do not include splittings if rot_period_sur  < 0
    incl : inclination angle (in degrees)

    activity: add an activity component, tuple (sigma,tau) where  sigma is the amplitude (in ppm) and  tau the characteristic time (in days) ; activity= None  if no activity is added (default case)
    granulation: add the granulation component (by default: True)

    OUTPUTS:
    time : time vector (in seconds)
    lc: ligth-curve
    nu: frequencies [muHz]
    pds: power density spectrum [ppm^2/muHz]
    mpds: mean power density spectrum  [ppm^2/muHz]
    par: adopted paramaters of the simulation
    seed: adopted value of the seed
    
    '''
	
    obs_par =  get_obs_par(mag, T, dt , pn_ref = pn_ref,  wn_ref = wn_ref, mag_ref = mag_ref,verbose = verbose, teff=teff)

    dnu = obs_par['frequency_resolution']
    n = obs_par['time_steps_number']
    W = obs_par['white_noise']
    nyq =  obs_par['nyquist']
    
    # frequency values [muHz], n-1 values, null frequency is excluded
    f = (np.arange(n/2-1)+1)*dnu
    b2m = 1./ obs_par['bolometric_coefficient'] # bolometric to measured amplitude coefficient

    modes, (mass, radius) = read_agsm(filename)

    star_par = {'mass': mass, 'teff' : teff, 'radius' : radius} 
  
    numax =  numaxref * (mass/radius**2) * math.sqrt(teffsun/teff)
##    deltanu = deltanusun * (mass/radius**3)
    deltanu = deltanusun * math.sqrt(mass/radius**3)

    OS,(Amax,Hmax,Gamma,width_env),modespar = osc_spectrum(starID, f,modes,numax,deltanu,teff,verbose=verbose,a=a,b=b, plot=plot, rot_period_sur = rot_period_sur , incl = incl )

    # Granulation spectrum (GS)
    if(granulation):
        GS, gran_par   = granulation_spectrum(f,numax,mass=mass,type=GST) 
        GSf,  gran_par  = granulation_spectrum(2.*nyq-f,numax,mass=mass,type=GST,verbose=verbose)  # Folded component of the GS
    else:
        GS,GSf = 0.,0.
        gran_par = {}

    if activity is None:
        AS = 0.
        ASf = 0.
        activity_par = {'sigma': 0., 'tau': 0.}
    else:
        AS = activity_spectrum(f,activity,verbose=verbose)
        ASf = activity_spectrum(2.*nyq-f,activity)
        activity_par = {'sigma': activity[0], 'tau': activity[1]}
        
    # mean power spectrum [ppm2/Hz]
    mpsd =  ( (OS * (b2m**2)  + GS  + GSf + AS + ASf ) * 1e6  *   (np.sinc(0.5*f/nyq))**2   +  2.*W**2 )  # [ppm^2/Hz] 

    time, ts , ps , seed =  mpsd2rts(f*1e-6,mpsd,seed=seed)

##    osc_par = (numax,deltanu,Amax,Hmax,Gamma,width_env,a,b,c)
    osc_par = {'numax' : numax, 'deltanu': deltanu, 'Amax' : Amax, 'Hmax' : Hmax, 'Gammamax': Gamma, 'width_envelop' : width_env, 'se_a': a, 'se_b': b }
   
    if(verbose):
        print ("numax [muHz], delta_nu [muHz], mass, radius, Teff [K]: %f , %f, %f, %f, %f") % (numax,deltanu,mass,radius,teff)
        print ("Hmax [ppm2/muHz], Amax [ppm], gamma [muHz], width_env [muHz]: %e , %f , %f, %f") % (Hmax,Amax,Gamma,width_env)
        print ("a= %f, b= %f") % (a,b)
        print ("b2m, white_noise  [ppm2/muHz]: %f %g")% ( b2m,2.*W**2*1e-6 )
        print ("times series, standard deviation [ppm]: %f") % np.std(ts)
        print ("theoretically expected standard deviation [ppm]: %f") %  math.sqrt(  np.sum(mpsd)*1e-6* f[0] ) 

    # output parameters
    opar = (star_par,obs_par,osc_par,gran_par,activity_par)

    return time,ts,f,ps*1e-6,mpsd*1e-6,opar,seed


def gen_up(starID, numax,dt,T, mag , delta_nu =  -1. , mass = -1. , seed = None, pn_ref = 7.7, wn_ref= 0., mag_ref = 6.,verbose = False, teff = 4800., DPI = -1.,  q = 0. , GST = 0 , incl = -1 , rot_f = 0.):
    '''
    Generate a simulated light-curve on the basis of the Universal Pattern
    
    time,ts,f,ps,mps,opar,seed = gen_up(numax,dt,T, mag, delta_nu =  -1. ,teff = 4800., DPI = -1.,  q = 0.,pn_ref = 7.7,mag_ref = 6., seed = None,verbose= False)
    
    INPUTS:

    starID : any number to identify the simulation, this is used only for the plots and the generated output files 
    numax : peak frequency [muHz]
    dt : sampling time [s]
    T:  duration of the time series [days]
    mag: star magnitude

    delta_nu :  mean large separtion [muHz], if negative, delta_nu is computed according to a scaling relation
    teff : effective temperature [K], default: 4800 K
    DPI : asymptotic period spacing [s], negative if no mixed modes are wanted
    q : coupling coefficient, default: q=0 (no coupling)

    pn_ref: photon-noise reference level  [ppm per hour]
    wn_ref: Non photonic white-noise reference level  [ppm per hour]
    mag_ref: reference magnitude for the white-noise levels
    seed: seed of the Random Number Generator (RNG)
    verbose : verbose mode if True

    OUTPUTS:
    time: the time values
    ts: the simulated time-series (flux fluctuations in ppm)
    f: frequency values [muHz]
    ps: simulated power spectrum [ppm2/muHz]
    mps: mean power spectrum [ppm2/muHz]
    opar: simulation parameters
    seed:  adopted value of the seed (chosen by the Random Number Generator if seed is not specified in input)

    Simulation (output) parameters:
    - H_env : height of the oscillation envelope  [ppm^2/muHz]
    - width_env : width of the envelope [muHz]
    - gamma : mode width (for pure acoutic modes) [muHz]
    - h_gran : height of the granulation  component
    - tau_gran : time-scale of the granulation
    - sigma_gran : rms brightness fluctuations associated with the granulation [ppm]
    - b2m : bolometric to measured flux conversion factor
    parameters = (numax,delta_nu,mass,teff,H_env,width_env,gran_par,b2m,wn)    

    '''

    obs_par =  get_obs_par(mag, T, dt , pn_ref = pn_ref,  wn_ref = wn_ref, mag_ref = mag_ref,verbose = verbose, teff=teff)

    dnu = obs_par['frequency_resolution']
    n = obs_par['time_steps_number']
    W = obs_par['white_noise']
    nyq =  obs_par['nyquist']

    # frequency values [muHz], n-1 values, null frequency is excluded
    f = (np.arange(n-1)+1)*dnu
    f = (np.arange(n/2-1)+1)*dnu
    b2m = 1./ obs_par['bolometric_coefficient'] # bolometric to measured amplitude coefficient
    
    # Mean large separation
    if (delta_nu <=0. ):
	    delta_nu = 0.274*numax**0.757 # ref. M13

    if (mass <=0.):
	    # mass estimated combining the "classical" scaling laws for numax et deltanu
	    mass = (numax/numaxref)**3. * (delta_nu/deltanusun)**(-4.) * (teff/teffsun)**(3./2.)

    radius = (numax/numaxref)*(delta_nu/deltanusun)**(-2) *(teff/teffsun)**(1./2.)

    H_env = 2.3* 2.03e7*numax**(-2.38) # [ppm2/muHz], Mosser sf2a 2013 , mutlipied by 3 to have the true Hmax (??)
    
    gamma = 0.19*(teff/4800.)**(10.8)   # Belkacem, sf2a, 2012
    width_env =  0.66*(numax**0.88)        # dnu_env = FWHM of the excess power envelope, see: Mosser et al. (2012 A&A 537 A30) - Table 2
    
    # building The Universal Pattern    
    UPm = UP.universal_pattern(delta_nu, numax, H_env,  f , nyq , verbose = verbose , teff = teff, DPI = DPI, q=q, gamma=gamma, width = width_env , rot_f = rot_f , beta = incl , epsg = 0.25)
    

    # Granulation spectrum (GS)
    GS, gran_par   = granulation_spectrum(f,numax,mass=mass,type=GST) 
    GSf,  gran_par  = granulation_spectrum(2.*nyq-f,numax,mass=mass,type=GST,verbose=verbose)  # Folded component of the GS
            

    # mean power spectrum [ppm2/Hz]
    mpsd =   (UPm * (b2m**2)  + GS  + GSf  ) * 1e6 *(np.sinc(0.5*f/nyq))**2   +  2.*W**2   #  

    time, ts , ps , seed =  mpsd2rts(f*1e-6,mpsd,seed=seed)

    star_par = {'mass': mass, 'teff' :  teff, 'radius': radius}
    osc_par = {'numax' : numax, 'deltanu': delta_nu, 'Hmax' : H_env, 'Gammamax': gamma, 'width_envelop' : width_env,'inclination': incl, 'rot_f': rot_f }
    activity_par = {'sigma': 0., 'tau': 0.}
    
    if(verbose):
        print ("numax [muHz], delta_nu [muHz], mass, Teff [K]: %f , %f, %f, %f") % (numax,delta_nu,mass,teff)
        print ("H_env [ppm2/muHz], width_env [muHz], gamma [muHz]: %e , %f , %f") % (H_env,width_env,gamma)
        print ("b2m, white_noise  [ppm2/muHz]: %f %g")% ( b2m,2.*W**2*1e-6 )
        print ("times series, standard deviation [ppm]: %f") % np.std(ts)
        print ("theoretically expected standard deviation [ppm]: %f") %  math.sqrt(  np.sum(mpsd)*1e-6* f[0] ) 

    # output parameters
    opar = (star_par,obs_par,osc_par,gran_par,activity_par)

    return time,ts,f,ps*1e-6,mpsd*1e-6,opar,seed



def savelc(time,lc,StarID,par,seed,path='',navg=1,lctype=0):
    '''

    savelc(time,lc,StarID,par,seed,path='')
    
    Save the light-curve in an ASCII file compatible with kepler and the SSI pipeline (TypeFile=8)

    time : time values
    lc : the light-curve
    StarID : ID of star (StarID must be >0)
    par : simulation parameters 
    seed: seed associated with the simulation
    path: where to save the ligth-curve
    navg: input light-curve values are averaged over navg consecutive values (default: navg = 1, i.e. no average)
          the sampling of the output light-curves will then be equal to dt*navg
    lctype: type of ligt-curve format, 
        type=0 : KASOC ASCII format
        type=1 : simple ASCII format
    '''


    if (navg > 1 ):
	n = lc.size/navg
	t = rebin1d(time[0:n*navg],n)/float(navg)
	lc = rebin1d(lc[0:n*navg],n)/float(navg)
    else:
	t = time
    	n = lc.size
    if(lctype==0):
        t = t/86400. # time in Julian days
    filename = path
    if(lctype==0):
        filename += ('kplr%10.10i') %  (StarID)
    else:
        filename += ('%10.10i') %  (StarID)

    f=open(filename+'.dat','w')
    f.write(('# seed  %i\n') % (seed))
    def ppar(par):
	n = len(par)
	i = 0 
	for u in par.items():
		f.write(' %s = %g' % u)
		if (i < n-1):
			f.write(', ')
		i += 1
	f.write('\n')
    f.write('# star parameters:')
    ppar(par[0])
    f.write('# observations parameters:')
    ppar(par[1])
    f.write('# oscillation parameters:')
    ppar(par[2])
    f.write('# granulation parameters:')
    ppar(par[3])
    f.write('# activity parameters:')
    ppar(par[4])
    f.write('# navg: %i\n' % (navg))
    if(lctype==0):
        f.write('# Time [julian days], Flux [ppm], Flag\n')
        for i in range(n):
            f.write( ("%25.15e %25.15e   0\n") % (t[i],lc[i]) )
    else:
        f.write('# Time [s], Flux\n')
        for i in range(n):
            f.write( ("%25.15e %25.15e\n") % (t[i],lc[i]*1e-6+1.) )
        
        
    f.close()
  

def genslc(n,f,mpsd,par, seed=None,path='', verbose=False,navg = 1):
	'''	
	Generate several light-curves and save them in a set of files
	Each simulated light-curve corresponds to a given realization.
	
	seed  = genslc(n,numax,seed=None,path='', .... )

	n: number of simulated light-curves 
	f: frequency values [muHz] (as returned by gen_up or gen_adipls)
	mps: mean power spectrum [ppm2/muHz]  (as returned by gen_up or gen_adipls)
	par: simulation parameters (as returned by gen_up or gen_adipls)

	path: directory where the light-curves will be stored
	seed: initial seed of the Random Number Generator (RNG). If seed=None, choose one randolmy
	verbose: if true, verbose mode is on
        navg: light-curve values are  averaged over navg consecutive values (default: navg = 1, i.e. no average). 
              the sampling of the output light-curves will then be equal to dt*navg


	Example:
	seed = 13434343
	time,ts,f,ps,mps,par,seed = gen_up(StarID, numax,dt,T, mag , seed = seed )
	seed = genslc(n,f,mps,par,seed=seed)

	'''

	if( seed == None):
	    # see is not specified, we choose a random value 
	    seed = np.random.random_integers(0,high=2**30)    
	# initialization of the state of the RNG
	np.random.seed(seed)
	seeds = np.random.random_integers(0,high=2**30,size=n)
	for i in range (n):
		StarID = i+1
		time, ts , ps, seedi =  mpsd2rts(f*1e-6,mpsd*1e6,seed=seeds[i])

		savelc(time,ts,StarID,par,seedi,path=path,navg=navg)

	return seed

def test_gen_up():
    # ----------------------------------------------
    # Simulation parameters
    #
    
    # numax [muHz]
    numax = 61.2

    # deltan_nu [muHz]
    delta_nu  = 5.72

    # DPI [s], asymptotic period spacing
    DPI = 232.20

    # coupling coefficient
    q = 0.27

    # effective temperature
    teff = 4800.
    
    # sampling time
    dt = 512.

    # once generated, light-curve values are averaged over navg consecutive individual values (default: navg = 1, i.e. no average
    # the sampling of the output light-curve will then be equal to dt*navg
    navg = 1

    # duration in  days
    T = 150. 

    # photon-noise reference level  [ppm.hour^(1/2)]
    pn_ref = 7.7

    # non-photonic white-noise reference level [ppm.hour^(1/2)]
    wn_ref = 0.

    # reference magnitude for the white-noise level 
    mag_ref = 6.

    # star magnitude
    mag = 12.

    # Seed of the RNG
    seed = None
    
    StarID = 1

    #
    # ----------------------------------------------

    time,ts,f,ps,mps,opar,seed = gen_up(StarID,numax,dt,T, mag , delta_nu = delta_nu, seed = seed, pn_ref = pn_ref, wn_ref = wn_ref , mag_ref = mag_ref , verbose = 1 , teff=teff, DPI = DPI , q = q , GST = 1)

        # save the light-curve
    savelc(time,ts,StarID,opar,seed,navg=navg)

    plt.ioff()

    plt.figure(1)
    plt.clf()
    plt.plot(f,mps)
    plt.xlabel(r'$\nu$ [$\mu$Hz]')
    plt.ylabel(r'[ppm$^2$/$\mu$Hz]')
    plt.axis(xmin=15,xmax=110)
    plt.savefig('test_gen_up_1.png')

    plt.figure(2)
    plt.clf()
    plt.plot(f,ps)
    plt.plot(f,mps,'r')
    plt.xlabel(r'$\nu$ [$\mu$Hz]')
    plt.ylabel(r'[ppm$^2$/$\mu$Hz]')
    plt.loglog()
    plt.axis(ymin=1,ymax=1e5,xmin=1e-1,xmax=300)
    plt.savefig('test_gen_up_2.png')


    plt.figure(3)
    plt.clf()
    plt.plot(time,ts)
    plt.savefig('test_gen_up_3.pdf')


#    plt.semilogy()
#    plt.loglog()

    plt.show(block=False)

    s = raw_input('Type ENTER to finish')
    
    return time,ts,f,ps,mps,opar

def test_gen_adipls():
    # ----------------------------------------------
    # Simulation parameters
    #
    
    # effective temperature
    teff = 5953.74
    
    # sampling time
    dt = 32.

    # duration in  days
    T = 150. 

    # photon-noise reference level  [ppm.hour^(1/2)]
    pn_ref = 7.7

    # non-photonic white-noise reference level [ppm.hour^(1/2)]
    wn_ref = 0.

    # reference magnitude for the white-noise level 
    mag_ref = 6.

    # star magnitude
    mag = 6.

    #  parameters a,b used for modelling surface effects
    a,b = -0.004369 , 3.275559
    
    # Seed of the RNG
    seed = None
    
    StarID = 2

    # Name of the .gsm generated by ADIPLS
    fname = 'test.gsm'

    #
    # ----------------------------------------------
    
    time,ts,f,ps,mps,opar,seed = gen_adipls(StarID, fname,teff,dt,T,mag,verbose=True,seed=seed,mag_ref=mag_ref,pn_ref=pn_ref,wn_ref=wn_ref, a=a,b=b,plot=True, rot_period_sur =  -1. , GST = 1 ) 

    # save the light-curve
    savelc(time,ts,StarID,opar,seed)

    plt.ioff()


    plt.figure(1)
    plt.clf()
    plt.plot(f,mps)
    plt.xlabel(r'$\nu$ [$\mu$Hz]')
    plt.ylabel(r'[ppm$^2$/$\mu$Hz]')
    plt.axis(xmin=500,xmax=3000)
    plt.savefig('test_gen_adipls_1.png')

    plt.figure(2)
    plt.clf()
    plt.plot(f,ps)
    plt.plot(f,mps,'r')
    plt.xlabel(r'$\nu$ [$\mu$Hz]')
    plt.ylabel(r'[ppm$^2$/$\mu$Hz]')
    plt.loglog()
    plt.axis(ymin=1e-2,ymax=1e2,xmin=10,xmax=5000)
    plt.savefig('test_gen_adipls_2.png')

    plt.figure(3)
    plt.clf()
    plt.plot(time,ts)
    plt.savefig('test_gen_adipls_3.pdf')


#    plt.semilogy()
#    plt.loglog()

    plt.show(block=False)

    s = raw_input('Type ENTER to finish')
    
    return time,ts,f,ps,mps,opar



## def test_single_mode():
    

##     # A :  mode amplitude  (arbitrary units)
##     A = 10.


##     #  nu0 :  mode frequency  [muHz]
##     nu0 = 3000.

##     # gamma : mode line-width  [muHz]
##     gamma = 10.

##     # white-noise (rms)
##     W = 0.0

##     # sampling time
##     dt = 50.

##     # duration in  days
##     T = 50. 

##     seed = 1999


##     #
##     gamma0=gamma*1e-6
##     nu00=nu0*1e-6 # mode frequency in Hz


##     T0 = T*86400.
##     # size of array of the time series
##     n = long(T0/(dt*2.))

##     # frequency resolution
##     dnu = 1./(2*n*dt)

##     # frequency values
##     f = (np.arange(n-1)+1)*dnu

##     # mode height
##     H = 2.*A**2/(math.pi*gamma0)

##     nyq = 1./(2.*dt) # Nyquist frequency

##     # mode profile (lorenztian profile):
##     x = 2.*(f-nu00)/gamma0
##     xp = 2.*(2.*nyq-f-nu00)/gamma0

##     # mean power spectrum
##     # the second term corresponds to the folded component
##     mpsd =   H/(1.+x**2) + H/(1.+xp**2) + 2.*W**2*dt


##     time, ts , ps =  mpsd2rts(f,mpsd,seed=seed)

##     print ("power spectrum, standard deviation: %f") % math.sqrt(np.sum(ps)*dnu)

##     print ("times series, standard deviation: %f") % np.std(ts)

##     plt.figure(0)
##     plt.clf()
##     plt.plot(time,ts)

##     plt.figure(1)
##     plt.clf()
##     plt.plot(f*1e3,ps)
##     plt.plot(f*1e3,mpsd)
##     plt.semilogy()

##     plt.show()
