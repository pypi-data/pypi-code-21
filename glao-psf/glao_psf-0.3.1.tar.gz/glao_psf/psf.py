# -*- coding: utf-8 -*-
"""  Structure function and average PSF calculator for astronomical imaging
  Reference:
  [1] Gavel, D. (2017). Point Spread Function for Ground Layer Adaptive Optics.
  arXiv:astro-ph.IM, 1706.00041. Retrieved from http://arxiv.org/abs/1706.00041
"""
import sys
import os
import platform
if 'VIRTUAL_ENV' in os.environ and platform.system() == 'Darwin':
    import matplotlib
    matplotlib.use('PDF') # to allow a virtual environment with no graphics back end
import matplotlib.pylab as plt
import numpy as np
from infoArray import InfoArray
import img
from StringIO import StringIO
from units import *
from oprint import pprint
import re
import warnings
import pandas as pd
import itertools
from collections import OrderedDict
import time
import h5py
import json
import random
from scipy.special import gamma, kv

# -------------------------- Classes --------------------------------

class Cn2_Profile(object):
    """The Profile class defines the atmospheric profile
    
    Instances contain
        Cn2 profile vs altitude
        the normalized Cn2 (normalized to sum to one)
        normalized altitude (normalized to mean height)
        computed r0, theta0
    Several valid profiles are pre-defined, but the caller can also
    specify with a 'name', 'Cn2' and 'h' arguments
    
    'HV' profiles requre keyword arguments 'r0' and 'theta0' and 'dh'
    Other profiles can optionally contain an 'r0' argument, in which case
    the profile is normalized (Cn2 is changed) to compute to that r0.
    """
    valid_profiles = ['CP Typical','MK Imaka','Cerro Pachon','Mauna Kea','Simple 1','Simple 2','Simple 2h_100']
    
    def __init__(self, profile='Simple 1', **kwargs):
        self.profile = profile
        self.make_profile(profile=self.profile,**kwargs)
        self.name = self.profile
        self.suppressWarnings = False
        if 'suppressWarnings' in kwargs:
            self.suppressWarnings = kwargs['suppressWarnings']
        self.warning = ''
    
    def pprint(self):
        pprint(self)
    
    def make_profile(self,profile,**kwargs):
        self.lam0 = self.lam = 0.55
        self.lam0_units = 'microns'
        self.lam_units = 'microns'
        self.Cn2_units = 'm^1/3 (Cn2*dh units)'
        self.r0_units = 'm'
        self.r00_units = 'm (at 0.55 microns)'
        self.h_units = 'm'
        self.sf_method = 'new'
        
        lam = self.lam0*units[self.lam0_units]

        if profile not in self.valid_profiles:
            self.profile_fromDatabase(profile)
            h,Cn2 = self.h,self.Cn2
        else:
            if profile in ['Cerro Pachon','Mauna Kea']:
                self.longName = profile
                rdir = os.path.dirname(__file__)
                filename = os.path.join(rdir,'data','cn2.csv')
                fp = open(filename)
                s = fp.read()
                fp.close()
                s = s.replace('\r','\n')
                u = np.genfromtxt(StringIO(s),delimiter=',',skip_header=3,dtype=float).transpose()
            if profile == 'CP Typical':
                self.longName = 'Gemini South site testing, typical profile'
                reference = """
                Andersen, D. R., Stoesz, J., Morris, S., Lloyd-Hart, M., Crampton, D., Butterley, T., ... Wilson, R. (2006).
                Performance Modeling of a Wide Field Ground Layer Adaptive Optics System.
                Publications of the Astronomical Society of the Pacific, 118(849), 1574-1590. http://doi.org/10.1086/509266
                """
                self.reference = re.sub(' +',' ',reference)
                h = np.array([1.,25,50,100,200,400,800,1600,5500])
                Cn2 = np.array([7.04, 2.25, 1.35, 1.24, 1.99, 2.87, 3.02, 1.75, 17.0])*10**(-14) # m^(1/3)
            if profile == 'MK Imaka':
                self.longName = 'Gemini North site testing, 50 percentile profile'
                reference = """
                Lai, O., Chun, M., Charles, J., Carlberg, R., Richer, H., Pazder, J., ... Vp, B. C. (2008).
                IMAKA : Imaging from Mauna KeA with an atmosphere corrected 1 square degree optical imager.
                Proc. of SPIE, 7015, 1-12. http://doi.org/10.1117/12.790114
                """
                self.reference = re.sub(' +',' ',reference)
                h = np.array(  [1., 70, 130., 200., 270, 330., 400., 450.])
                Cn2 = np.array([20.,2.,  0.6, 0.4, 0.35, 0.14, 0.12, 0.03 ])*10**(-14)
            if profile == 'Simple 1':
                self.longName = "Single layer atmosphere"
                if 'layer_height' in kwargs:
                    h1 = kwargs['layer_height']
                else:
                    h1 = 1.
                h =  [ h1 ]
                Cn2 = [ 1. ]
                r0 = 20*cm
                h = np.array(h)*km
                k = 2*np.pi/lam
                Cn2 = np.array(Cn2)*(1./0.423)*r0**(-5./3.)*k**(-2)
            elif profile == 'Simple 2':
                self.longName = 'Two layer atmosphere with 68% of Cn2 in ground layer'
                h = [0., 1.5] # km
                Cn2 = [0.68,0.32] # %
                r0 = 20*cm
                k = 2*np.pi/lam
                Cn2 = np.array(Cn2)*(1./0.423)*r0**(-5./3.)*k**(-2)
                h = np.array(h)*km
            elif profile == 'Simple 2h_100':
                self.longName = 'Two layer atmosphere with 68% of Cn2 at 100m above ground'
                h = [0.1, 1.5] # km
                Cn2 = [0.68,0.32] # %
                r0 = 20*cm
                k = 2*np.pi/lam
                h = np.array(h)*km
                Cn2 = np.array(Cn2)*(1./0.423)*r0**(-5./3.)*k**(-2)
            elif profile == 'Cerro Pachon':
                self.longName = 'Cerro Pachon, Chile, location of Gemini Observatory'
                h, Cn2 = u[0:2,0:7]
                r0 = 0.15
                k = 2*np.pi/lam
                Cn2 = Cn2/(0.423*k**2*r0**(5./3.))
                h = h*km
            elif profile == 'Mauna Kea':
                self.longName = 'Mauna Kea, Hawaii, location of Keck telescopes'
                h, Cn2 = u[3:5,0:10]
                r0 = 0.2
                k = 2*np.pi/lam
                Cn2 = Cn2/(0.423*k**2*r0**(5./3.))
                h = h*km
            
            self.h,self.Cn2 = h,Cn2
        
        self.r0_calc()
        self.r00 = r00 = self.r0
        if 'L0' in kwargs:
            self.L0 = kwargs['L0']
            self.L0_units = 'm'
            self.K0 = 2*np.pi/self.L0
            self.K0_units = 'm^-1'
        else:
            self.L0 = 'Infinity'
            self.K0 = 0.
        
        if 'lam' in kwargs:
            self.lam = kwargs['lam']
        
        if 'sf_method' in kwargs:
            self.sf_method = kwargs['sf_method']
            
        # If r0 is specified, it is r00, which is r0 at 0.55 microns.
        # Scale the profile, Cn2, so that it integrates to
        # the specified r00 instead of r0. Then, recalculate
        # r0 for the specified wavelength, lam.
        
        if 'r0' in kwargs:
            self.r00 = r00 = kwargs['r0']
        
        self.Cn2 = Cn2 = Cn2*(r00/self.r0)**(-5./3.)
        self.r0_calc()

        self.Cn2_bar = Cn2_bar = Cn2/np.sum(Cn2)
        h_bar = np.sum(Cn2_bar*h**(5./3.))**(3./5.)
        h_bar = [1,h_bar][h_bar>0]
        self.h_bar = h_bar
        self.h_bar_units = 'm'
        self.xi = h/h_bar
        if not hasattr(self,'r0'):
            self.r0_calc()
        if not hasattr(self,'theta0'):
            self.theta0_calc()
        
        # calculate the constants that will go
        # into calculating the structure function
        
        c0 = 8.*np.sqrt(2.)*((3./5.)*gamma(6./5.))**(5./6.)
        c1 = 16.*np.sqrt(2.)*((3./5.)*gamma(6./5.))**(5./6.)
        c2 = 5.*np.pi**(5./6.)
        c3 = 3.*gamma(11./6.)
        c4 = 5.*np.pi**(5./3.)*gamma(-5./6.)
        
        self.cons = [c0,c1,c2,c3,c4]
        self.make_PSF0()

    def profile_fromDatabase(self,profile,dbFile = 'Cn2_profiles.hd5'):
        """Read in a profile from a database of profiles
        argument:
            profile is a string of the form '<site> <tile>'. For example 'Armazones median' or 'Maunakea 13N 75%'
        keyword:
            dbFile is the HDF5 file that contains seeing profiles
        """
        rdir = os.path.dirname(__file__)
        dbFile = os.path.join(rdir,'data',dbFile)
        site,tile = profile.rsplit(' ',1)
        self.site,self.tile = site,tile
        self.databaseFile = dbFile
        store = pd.HDFStore(dbFile)
        # first, look for a specific table in the store
        name = 'df_%s'%site
        if name in store:
            df = store[name]
            metadata = store.get_storer(name).attrs.metadata
            store.close()
            self.databaseMetadata = metadata
            sel = df[(df.site == site) & (df.tile == tile)].iloc[0]
            h = np.array(sel.Altitude)
            Cn2 = np.array(sel.Cn2_dh)
        else:
            df = store['df']
            metadata = store.get_storer('df').attrs.metadata
            store.close()
            self.databaseMetadata = metadata
            sel = df[(df.Site == site) & (df.tile == tile)].iloc[0]
            h = list(sel.index[2:-2])
            h = map(lambda x: float(x.replace('GL','0m').replace('km','000').replace('m','')),h)
            h = np.array(h)
            Cn2 = np.array(list(sel.iloc[2:-2]))*1.e-14
        
        self.h,self.Cn2 = h,Cn2

    def r0_calc(self):
        """Compute r0 from the profile
        """
        Cn2,h,lam = self.Cn2,self.h,self.lam*microns
        k = 2*np.pi/lam
        self.r0 = (0.423*k**2*Cn2.sum())**(-3./5.)
        self.r0_units = 'm'
        return self.r0,self.r0_units
    
    def theta0_calc(self):
        """Compute theta0 from the profile
        """
        Cn2,h,lam = self.Cn2,self.h,self.lam*microns
        k = 2*np.pi/lam
        self.theta0 = (2.914*k**2*(Cn2*h**(5./3.)).sum())**(-3./5.)/arcsec
        self.theta0_units = 'arcsec'
        return self.theta0,self.theta0_units
    
    def _smat_prep_1_(self,c,dm_conjugate=0.,wfs_conjugate=0.,act_spacing=None):
        """first step in preparing to calculate the S matrix
        
        Argument:
            c - an instance of a Constellation object
        
        Keywords:
            dm_conjugate - conjugate altidude of the dm, meters
            wfs_conjugate - conjugate altitude of the wfs, meters
                       (results in a shift of thw wfs measurements)
            act_spacing - the actuator spacing, in meters (optional if modeling the DM Nyquist cutoff)
        """
        self.constellation = c
        assert isinstance(c,Constellation)
        theta0 = self.theta0*units[self.theta0_units]
        alpha = c.alpha
        
        self.dm_conjugate = dm_conjugate
        self.dm_conjugate_units = 'm'
        self.wfs_conjugate = wfs_conjugate
        self.wfs_conjugate_units = 'm'
        
        h_bar = self.h_bar
        zc, zs = self.dm_conjugate, self.wfs_conjugate
        r0,L0,K0 = self.r0,self.L0,self.K0
        xi_c = zc/h_bar
        xi_s = zs/h_bar
        eta = alpha / theta0
        if L0 == 'Infinity':
            l0 = L0
            k0 = 0.
        else:
            l0 = L0 / r0
            k0 = K0*r0
        
        self.xi_c, self.xi_s,c.eta = xi_c,xi_s,eta
        self.l0, self.k0 = l0,k0
        
        # normalized varaibles:
        #   Cn2_bar - Cn2 profile normalized to sum to one
        #   xi, xi_c, xi_s - altitude normalized to h_bar
        #   eta - guide star positions normalized to theta0
        #   l0 - outer scale normalized to r0
        #   k0 = K0 normalized to r0 
        #   mu - separation argument for structure function, normalized to r0
        
        if act_spacing is not None:
            mu_act = act_spacing/r0
            self.act_spacing = act_spacing
            self.act_spacing_units = self.r0_units
            self.mu_act = mu_act
            self.spatialFilter = True
        else:
            self.spatialFilter = False

    def _smat_prep_2_(self,r_lim='calc',n=512):
        """creates the S matrix
        """
        self.n_fine = n
        c = self.constellation
        xi_h,xi_c,xi_s = self.xi, self.xi_c, self.xi_s
        Cn2_bar = self.Cn2_bar
        r0 = self.r0
        eta,N = c.eta, c.N
        p314 = self.cons[0]**(-3./5.) # 0.314
        
        self.warning = ''
        if r_lim == 'calc':
            r_lim = self.r0*(n/8.)
            if r_lim < c.radius*arcmin*self.h_bar:
                dr = 2*r_lim/float(n)
                warn1 = 'WARNING: structure function extent %0.2f arcmin is less than constellation radius %0.2f arcmin at h_bar'%(r_lim,c.radius*arcmin*self.h_bar)
                warn2 = 'suggest increasing n (now %d) to >%d'%(n,2*c.radius*arcmin*self.h_bar/dr)
                self.warning = warn1+'\n'+warn2
                if not self.suppressWarnings:
                    print self.warning
        else:
            if r_lim/float(n) < self.r0/8.:
                warn1 = 'WARNING: structure function does not sample r0 well'
                warn2 = '  suggest increasing n (now %d) to >%d'%(n,8.*r_lim/self.r0)
                self.warning = warn1+'\n'+warn2
                if not self.suppressWarnings:
                    print self.warning
        self.r_lim = r_lim
        self.dr = dr = 2*r_lim/float(n)
        r = np.arange(-r_lim,r_lim,dr)
        mu = r/r0
        dmu = dr/r0
        mu_x,mu_y = np.meshgrid(mu,mu)
        S = np.zeros((N+1,N+1,n,n)) # Structure Function
        S0 = np.zeros((N+1,N+1,n,n)) # Correlation Function
        # [1] equation (59)
        for xi,Cn2b in zip(xi_h,Cn2_bar):
            for j in range(N+1):
                delta_j = [0,1][j==0] # Kroneker delta
                for jp in range(N+1):
                    delta_jp = [0,1][jp==0]
                    bx = p314*((eta[j,0] - eta[jp,0])*(xi-xi_s) + eta[0,0]*(xi_s - xi_c)*(delta_j - delta_jp))
                    by = p314*((eta[j,1] - eta[jp,1])*(xi-xi_s) + eta[0,1]*(xi_s - xi_c)*(delta_j - delta_jp))
                    ax = mu_x + bx
                    ay = mu_y + by
                    a = np.sqrt(ax**2 + ay**2)
                    b = np.sqrt(bx**2 + by**2)
                    if self.sf_method == 'original':
                        sfa = self._sf(a)
                    elif self.sf_method == 'new':
                        sfa = self._sf2([bx,by])
                    sfb = self._sf(b)
                    S[j,jp,:,:] += Cn2b*(sfa-sfb)
                    S0[j,jp,:,:] += -0.5*Cn2b*sfa
                        
        self.S_original = S.copy()
        if self.spatialFilter and self.mu_act != 0.:
            # [1] equation (67)
            # note, this is done only for the structure function
            # --- wrong ---
            # nyquist = (n/2)/(self.mu_act/dmu) # units: cycles per pixel
            # mu_r = np.sqrt(mu_x**2+mu_y**2) # units: r0
            # f = 1./(1. + np.exp((mu_r-nyquist)/(2*dmu)))
            # --- above is wrong, redoing! ---
            nyquist = 0.5/self.act_spacing # cycles per meter
            df = 1./(n*dr)
            fx = (np.arange(n)-n/2)*df
            fx,fy = np.meshgrid(fx,fx)
            fr = np.sqrt(fx**2+fy**2) +2.*df 
            f = 1./(1. + np.exp((fr - nyquist)/df))
            #f = np.where( mu_r < nyquist,1,0)
            #f =  np.where(np.logical_and( np.abs(mu_x) < nyquist, np.abs(mu_y) < nyquist ),1,0)
            h = 1 - f
            h = InfoArray(h,name='spatialFilter',
                          dx = df, dx_units = 'cycles per meter',
                          nyquist = nyquist, nyquist_units = 'cycles per meter',
                          act_spacing = self.act_spacing, spacing_units = self.r0_units)
            self.spatialFilter = h
            # ***Test*** h is a delta function, allowing all spatial frequencies
            # This should result in no AO correction
            #print 'Debug: Testing h = delta function'
            #h = 1.
            for j in range(N+1):
                for jp in range(N+1):
                    if j == 0 and jp == 0:
                        R = Q = 0.
                    else:
                        Q = img.ft(S[j,jp,:,:])*h
                        if j != 0 and jp != 0:
                            R = Q*h
                            R = img.ftinv(R).real
                            R = R[n/2,n/2] - R
                            Q = img.ftinv(Q).real
                            Q = Q[n/2,n/2] - Q
                            R = Q - R
                        else:
                            R = 0.
                            Q = img.ftinv(Q).real
                            Q = Q[n/2,n/2] - Q
                    S[j,jp,:,:] += Q + R
        self.S = S
        self.S0 = S0
        self.mu_x,self.mu_y = mu_x,mu_y
        self.dr = r[1]-r[0]
        self.dr_units = 'm'
        self.dmu = dmu
        self.r_x,self.r_y = np.meshgrid(r,r)
        self.r_x_units = self.r_y_units = 'm'
        
    def make_S(self,constellation,r_lim='calc',n=512,dm_conjugate=0.,wfs_conjugate=0.,act_spacing=None):
        """Make the S matrix given the guide star constellation
        
        Parameters:
            constellation - a constellation object
            r_lim - the upper limit to the shift, in meters.
                Default is to calculate this internally based on the
                guide star separation and telescope size
            n - the fine grid (number of fine pixels from -r_lim to +r_lim in the structure functios)
            dm_conjugate - conjugate altitude of the DM, in meters
            wfs_conjugate - conjugate altitude of the wavefront sensor, in meters
            act_spacing - the actuator spacing, in meters (optional if modeling the DM Nyquist cutoff).
        """
        self._smat_prep_1_(constellation,dm_conjugate,wfs_conjugate,act_spacing=act_spacing)
        self._smat_prep_2_(r_lim,n)
    
    def make_PSF(self,w, constellation=None, **kwargs):
        """Make the PSF (point spread function), and incidentally, the MTF (modulation transfer function)
        given a set of weights on the guide star measurements.
            
        Parameters:
            w - guide star weight vector (size equal to number of guidestars). The weights must sum to one.

        Keyword arguments:
            constellation - guide star constellation
            kwargs - keyword arguments to the Constellation constructor and to the S matrix generator (self.make_S)
        """
        # check to see if the constellation is provided. If so, create a new S matrix
        c_kwargs = ['ngs','radius','geometry','rot','field_point']
        s_kwargs = ['r_lim','n','dm_conjugate','wfs_conjugate','spatialFilter']
        
        if constellation is not None:
            fkwargs = dict_filter(kwargs,s_kwargs)
            self.make_S(constellation,**fkwargs)
        
        # if we don't have a constellation, then we need to make one using the keyword parameters
        if not hasattr(self,'constellation'):
            fkwargs = dict_filter(kwargs,c_kwargs)
            constellation = Constellation(**fkwargs)
            fkwargs = dict_filter(kwargs,s_kwargs)
            self.make_S(constellation,**fkwargs)
        
        # check to see if the field point needs adjusting. field_point is in arcmin
        if 'field_point' in kwargs:
            field_point = np.array(kwargs['field_point'])
            if not np.isclose(field_point,self.constellation.field_point).all():
                self.constellation.field_point = field_point
                self.constellation.alpha[0,:] = field_point*arcmin
            fkwargs = dict_filter(kwargs,s_kwargs)
            self.make_S(self.constellation,**fkwargs)

        N = self.constellation.N
        w = np.array(w)
        if len(w) == N:
            wsum = w.sum()
            w = np.append([-1],w)
        elif len(w) == N+1:
            wsum = w[1:].sum()
        
        if len(w) != N+1:
            raise Exception,'length of w must equal the number of guidestars in the constellation %d'%N
        if not np.isclose(wsum,1.):
            raise Exception,'sum of weights =%0.2f; it is supposed to equal one'%wsum
        
        self.w = w
        S,S0 = self.S,self.S0
        N1,N1,n,n = S.shape
        lam,dr = self.lam*microns, self.dr
        
        D = np.zeros((n,n)) # Structure Function
        C = np.zeros((n,n)) # Correlation Function
        for j in range(N1):
            for jp in range(N1):
                D += w[j]*w[jp]*S[j,jp]
                C += w[j]*w[jp]*S0[j,jp]
        # check positivity of D
        frac_below_zero = np.where(D<0)[0].size/float(D.size)
        if frac_below_zero > 0.02:
            print '<psf.py make_PSF> WARNING %5.2f%% of structure function is negative'%(100.*frac_below_zero)
        Dtele = 20.*self.r0
        u = np.sqrt(self.r_x**2 + self.r_y**2)/Dtele
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            tau = (2./np.pi)*(np.arccos(u) - u*np.sqrt(1-u**2))
        tau = np.nan_to_num(tau)
        MTF = np.exp(-0.5*D)*tau
        fpx,fpy = np.round(self.constellation.field_point,2)
        name = r' $C_n^2$="%s"  $N_{gs}=%d_{\rm %s}$, $\Theta=%g^\prime$, $\theta=(%g,\,%g)$, $\lambda=%g\mu m$'%(self.profile,N,self.constellation.geometry,self.constellation.radius,fpx,fpy,np.round(self.lam,2))
        MTF = InfoArray(MTF,'MTF',sub=name,dx=self.dr,dx_units='meters',axis_names=[r'$r_x$',r'$r_y$'],
                        profile=self.profile,ngs=self.constellation.N)
        PSF = oft(MTF)
        dth = lam/(n*dr)/arcsec
        PSF = InfoArray(PSF,'PSF',sub=name,dx=dth,dx_units='arcsec',
                        wavelength=lam/microns,wavelength_units='microns',
                        r0 = self.r0, r0_units = self.r0_units,
                        axis_names=[r'$\theta_x$',r'$\theta_y$'],
                        profile = self.profile,AO = 'on',
                        ngs=self.constellation.N)
        th = np.arange(-n/2,n/2)*dth
        # Normalize the PSF to ~integrate~ to one
        PSF /= PSF.sum()*dth**2
        # calculate King's Equivalent Noise Area
        # (King, I. R. (1983). Accuracy of Measurement of Star Images on a Pixel Array. Publications of the Astronomical Society of the Pacific, 95(February), 163–168.)
        PSF.ena = dth**2/np.sum((PSF/PSF.sum())**2)
        PSF.ena_units = 'arcsec^2'
        PSF.ena_r = np.sqrt(PSF.ena/np.pi)
        PSF.ena_r_units = 'ENA radius, arcsec'
        PSF.calc_ee(0.5)
        PSF.calc_ee(0.8)
        
        self.dth, self.th = dth, th
        self.dth_units = self.th_units = 'arcsec'
        #PSF[n/2,n/2] = PSF[n/2,n/2+1] + (PSF[n/2,n/2+1]-PSF[n/2,n/2+2])/3.
        
        self.D,self.C = D,C
        self.MTF,self.PSF,self.tau = MTF,PSF,tau
    
    def _sf(self,r):
        """The finite outer scale structure function
        """
        c0,c1,c2,c3,c4 = self.cons
        k0 = self.k0
        if k0 == 0:
            return c0*r**(5./3.)
        eps = 1.e-16
        r += eps
        sf = c1*(c2*(k0*r)**(5./6.)*kv(5./6.,2*k0*np.pi*r)-c3) / (c4*k0**(5./3.))
        return sf
    
    def _sf2(self,b):
        """Generate finite outer scale structure function
        at a shift D(r+b), b = [bx,by], using a
        pre-computed structure function D(r)
        """
        n = self.n_fine
        if not hasattr(self,'n_bar'): # the size of the master array
            self.n_bar = n*2
        n_bar = self.n_bar
        if not hasattr(self,'D2'):
            #r = np.arange(-self.r_lim,self.r_lim,self.dr)
            r = (np.arange(n_bar)-n_bar/2)*self.dr
            mu = r/self.r0
            mu_x,mu_y = np.meshgrid(mu,mu)
            mu = np.sqrt(mu_x**2+mu_y**2)
            self.D2 = self._sf(mu)
        D2,dmu = self.D2,self.dmu
        b = np.array(b)
        s = np.round(b/dmu).astype(int)
        #indx = range(s[0],s[0]+n)
        #indy = range(s[1],s[1]+n)
        sx,sy = s
        indx = range(sx+n_bar/2-n/2,sx+n_bar/2+n/2)
        indy = range(sy+n_bar/2-n/2,sy+n_bar/2+n/2)
        try:
            sf = D2.take(indx,axis=0,mode='raise')
            sf = sf.take(indy,axis=1,mode='raise')
        except:
            #print '<psf._sf2> need to increase size of master array'
            #self.n_bar = 4*self.n_bar
            self.n_bar = (int(2.4*self.n_bar)//2)*2
            del self.D2
            return self._sf2(b)
        return sf
    
    def make_PSF0(self,n=512,r_lim='calc'):
        """Make the diffration-limited and seeing limited PSFs and MTFs
        """
        if hasattr(self,'n_fine'):
            n = self.n_fine
        else:
            self.n_fine = n
            r0,L0,K0 = self.r0,self.L0,self.K0
            if r_lim == 'calc':
                r_lim = r0*(n/8.)
            else:
                if r_lim/float(n) < r0/8.:
                    print 'WARNING: structure function does not sample r0 well'
                    print '  suggest increasing n (now %d) to >%d'%(n,8.*r_lim/r0)
            dr = 2*r_lim/float(n)
            r = np.arange(-r_lim,r_lim,dr)
            mu = r/r0
            mu_x,mu_y = np.meshgrid(mu,mu)
            if L0 == 'Infinity':
                l0 = L0
                k0 = 0
            else:
                l0 = L0/r0
                k0 = K0*r0
            self.mu_x,self.mu_y = mu_x,mu_y
            self.dr = r[1]-r[0]
            self.dr_units = 'm'
            self.dmu = self.dr/r0
            self.r_x,self.r_y = np.meshgrid(r,r)
            self.r_x_units = self.r_y_units = 'm'
            self.l0,self.k0 = l0,k0

        xi, Cn2_bar = self.xi, self.Cn2_bar
        mu_x, mu_y = self.mu_x, self.mu_y
        lam = self.lam*microns
        n,dr = self.n_fine,self.dr
        
        D = np.zeros((n,n))
        mu = np.sqrt(mu_x**2+mu_y**2)

        sfmu = self._sf(mu)
        for xi,Cn2b in zip(xi,Cn2_bar):
            D += Cn2b*sfmu
        self.D_seeing = D
        MTF = np.exp(-0.5*D)
        name = r' $C_n^2=$"%s"  $r_0=%gm$, $\lambda=%g\mu m$'%(self.profile,np.round(self.r0,2),np.round(self.lam,2))
        MTF = InfoArray(MTF,r'${\rm MTF}_{\rm seeing}$',sub=name,dx=self.dr,dx_units='meters',
                        axis_names=[r'$r_x$',r'$r_y$'])
        PSF = oft(MTF)
        dth = lam/(n*dr)/arcsec
        PSF = InfoArray(PSF,r'${\rm PSF}_{\rm seeing}$',sub=name,dx=dth,dx_units='arcsec',
                        wavelength=lam/microns,wavelength_units='microns',
                        r0 = self.r0, r0_units = self.r0_units, AO = 'off',
                        axis_names=[r'$\theta_x$',r'$\theta_y$'])
        # Normalize the PSF to ~integrate~ to one
        PSF /= PSF.sum()*dth**2
        # calculate King's Equivalent Noise Area
        # (King, I. R. (1983). Accuracy of Measurement of Star Images on a Pixel Array. Publications of the Astronomical Society of the Pacific, 95(February), 163–168.)
        PSF.ena = dth**2/np.sum((PSF/PSF.sum())**2)
        PSF.ena_units = 'arcsec^2'
        PSF.ena_r = np.sqrt(PSF.ena/np.pi)
        PSF.ena_r_units = 'ENA radius, arcsec'
        PSF.calc_ee(0.5)
        PSF.calc_ee(0.8)

        self.MTF_seeing, self.PSF_seeing = MTF,PSF

        Dtele = 20.*self.r0
        u = np.sqrt(self.r_x**2 + self.r_y**2)/Dtele
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            tau = (2./np.pi)*(np.arccos(u) - u*np.sqrt(1-u**2))
        tau = np.nan_to_num(tau)
        tau = InfoArray(tau,r'${\rm MTF}_{\rm dl}$',sub=name,dx=self.dr,dx_units='meters',
                        axis_names=[r'$r_x$',r'$r_y$'])
        self.MTF_dl = tau
        PSF_dl = oft(tau)
        self.PSF_dl = InfoArray(PSF_dl,r'${\rm PSF}_{\rm dl}$',sub=name,dx=dth,dx_units='arcsec',
                        axis_names=[r'$\theta_x$',r'$\theta_y$'])
    
    def profile_plot(self,altscale='log',cn2scale='log',drawstyle='steps'):
        """plot the profile and cumulative Cn2 profile
        Keywords:
            altscale - altitude scale; can be 'linear' or 'log'
            cn2scale - Cn2 axis scale; can be 'linear' or 'log'
            drawstyle - draw style for the cumulative graph: can be 'default' or 'steps'
            (Cn2 draw style is bar, with dot at end)
        """
        h,Cn2,Cn2_bar = self.h, self.Cn2, self.Cn2_bar
        cumProfile = []
        a = 0.
        for c in Cn2_bar:
            a += c
            cumProfile.append(a)
        cumProfile = np.array(cumProfile)
    
        plt.subplot(121)
        if altscale == 'log':
            plt.barh(h,Cn2/10**(-14),log=True,height=h*.05)
        else:
            plt.barh(h,Cn2/10**(-14),height = h.max()*.005)
        plt.plot(Cn2/10**(-14),h,'bo')
        plt.xlabel(r'$C_n^2$, $\times 10^{-14} m^{1/3}$')
        plt.ylabel('Altitude, meters')
        plt.yscale(altscale)
        plt.xscale(cn2scale)
        plt.ylim(0.9,10000.)
        plt.grid('on')
    
        plt.subplot(122)
        cumProfile = np.append([0],cumProfile)
        h = np.append([.9],h)
        plt.plot(cumProfile*100,h,linewidth=3,drawstyle=drawstyle)
        plt.xlabel(r'Accumulated percentage of $C_n^2$')
        plt.ylabel('Altitude, meters')
        plt.ylim(0.9,10000.)
        plt.yscale(altscale)
        plt.xlim(0,100)
        plt.grid('on')
        plt.subplots_adjust(top=0.92,bottom=0.1, left=0.15,right=0.95,hspace=0.25,wspace=0.35)        
    
        plt.suptitle(r'$C_n^2$ profile: "%s"'%self.profile,fontsize=14)

    def graph(self, which='structure',type='line',over=False,linestyle=None,color=None,linewidth=None,label='',dots=False, normalized_r=False):
        """graph one of the characteristic functions, Structure function or Correlation function.
        
        keyword:
            which - 'structure' or 'correlation'
            type - the type of graph, either 'line' (lineout) or 'grey' (2-d image greyscale)
            over - for lineout, this allows multiple overplots. First call should be False, then True for subsequent overplots
            label - if multiple overplots, the text for a legend (call plt.legend() after the last overplot)
        """
        assert which in ['structure','correlation']
        assert type in ['line','grey']
                    
        n,n = self.D.shape
        title = 'Profile: "%s", $N_{GS} =$ %d %s'%(self.name,self.constellation.N,self.constellation.geometry)
        if which == 'structure':
            P = self.D
            ylabel = r'Structure Function ${\cal D}_{\psi_r}(r)$, radians$^2$ @ $\lambda = %0.2f\, {\mu}m$'%(self.lam*units[self.lam_units]/microns)
        elif which == 'correlation':
            P = self.C
            ylabel = r'Correlation Function ${\cal C}_{\psi_r}(r)$, radians$^2$'
        if normalized_r:
            xlabel = r'normalized separation, $\mu=r/r_0$'
        else:
            xlabel = r'$r$, meters'
        if type == 'line':
            P = P[n/2,n/2+1:]
            r = self.r_x[n/2,n/2+1:]
            mu = self.mu_x[n/2,n/2+1:]
            if normalized_r:
                r = mu
            if which == 'structure' and not over:
                label0 = r'$6.88(r/r_0)^{5/3}$'
                plt.plot(r,6.88*mu**(5./3.),'k--',label=label0)                
            line, = plt.plot(r,P,linestyle=linestyle,color=color,linewidth=linewidth,label=label)
            color = line.get_color()
            if dots: plt.plot(r,P,'.',color=color)
            if which == 'structure':
                plt.xscale('log')
                plt.yscale('log')
            if not over:
                plt.grid('on',which='both')
                plt.title(title)
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
        elif type == 'grey':
            print 'type=grey not implemented yet'
    
    def showPSF(self,scale='log',which='both'):
        """Display PSF, and optionally, PSF_seeing, with (optionally) the Equiavlent Noise Area circled
        
        Keyword:
            scale = 'linear' or 'log'
            which = 'AO', 'seeing', or 'both'
        """
        if which == 'AO': PSFset = [self.PSF]
        if which == 'seeing': PSFset = [self.PSF_seeing]
        if which == 'both': PSFset = [self.PSF,self.PSF_seeing]
        
        for PSF in PSFset:
            if scale == 'log':
                PSF = np.log(PSF)
            PSF.show()
            n,m = PSF.shape
            dx = PSF.dx
            r = PSF.ena_r
            th = np.linspace(-np.pi,np.pi)
            x,y = r*np.sin(th),r*np.cos(th)
            plt.plot(x,y,'r')
            plt.xlim(-dx*n/2,dx*n/2)
            plt.ylim(-dx*m/2,dx*m/2)
        
class Constellation(object):
    """Defines the locations of the guide stars
    
    arguments:
        ngs = number of guide stars
        radius = radius of guide star constellation, arcmin
        geometry = 'circle', 'wheel', 'grid'
            ('wheel' is a circle with one guidestar in the middle)
            default is 'wheel'
        rot = rotation of the constellation on-sky, degrees
        field_point = position of the science field position, arcmin
    """
    def __init__(self,ngs=1,radius=10,geometry='wheel',rot=0., field_point=[0.,0.]):
        N = ngs
        radius = radius*arcmin
        rot = rot*degrees
        self.name = 'Guide star constellation'
        alpha = np.zeros((N+1,2))
        if geometry == 'circle':
            for k in range(1,N+1):
                theta = k*2*np.pi/float(N) + rot
                alpha[k,:] = [radius*np.cos(theta),radius*np.sin(theta)]
        elif geometry == 'wheel':
            alpha[1,:] = [0,0]
            for k in range(2,N+1):
                theta = k*2*np.pi/float(N-1) + rot
                alpha[k,:] = [radius*np.cos(theta),radius*np.sin(theta)]
        elif geometry == 'grid':
            assert N in [4,9,16] # only allowable grid patterns
            
            n = np.sqrt(N).astype(int)
            q = np.arange(n) - (n-1)/2.
            spacing = (2.*radius/np.sqrt(2))/float(n-1)
            k = 1
            for x in q:
                for y in q:
                    r = np.sqrt(x**2+y**2)*spacing
                    theta = np.arctan2(x,y) + rot
                    alpha[k,:] = [r*np.cos(theta),r*np.sin(theta)]
                    k = k+1
        self.field_point = np.array(field_point)
        alpha[0,:] = np.array(field_point)*arcmin
        
        self.N = N
        self.N_units = 'number of guide stars'
        self.geometry = geometry
        self.radius = radius/arcmin
        self.radius_units = 'arcmin'
        self.rotation = rot/degrees
        self.rotation_units = 'degrees'
        self.alpha = alpha
        self.alpha_units = 'radians'
        self.field_point = field_point
        self.field_point_units = 'arcmin'
    
    def graph(self,field_points = None,colors={}):
        """Graph the constellation of guidestars and the field point
        Keyword:
            Field_points = a list of [x,y] field points to graph instead of the one associated with the constellation
        """
        default_colors = {'guidestar':'orange',
                  'field point':'cyan',
                  'background':'black',
                  'axes':'grey',
                  'grid':'darkred'}
        default_colors.update(colors)
        colors = default_colors
        x,y = self.alpha.transpose()/arcmin
        r = max(np.abs(x).max(),np.abs(y).max())*1.1
        plt.plot(x[1:],y[1:],'*',color=colors['guidestar'],label='guidestar')
        if field_points is None:
            plt.plot(x[0],y[0],'o',color=colors['field point'],label='field point')
        else:
            label = 'field point'
            for point in field_points:
                plt.plot(point[0],point[1],'x',color=colors['field point'],label=label)
                label = None
        plt.xlim(-r,r)
        plt.ylim(-r,r)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.axes().set_aspect('equal')
        plt.grid('on',color=colors['grid'])
        plt.plot([-r,r],[0,0],colors['axes'])
        plt.plot([0,0],[-r,r],colors['axes'])
        #plt.gca().set_facecolor(colors['background'])
        plt.xlabel(r'$\theta_x$, arcmin')
        plt.ylabel(r'$\theta_y$, arcmin')
        plt.title(self.name)

    def pprint(self):
        pprint(self)

# --------------------------- Helper Routines -------------------------------

def progress_bar(n,N):
    """This creates and maintains a progress bar to show the status of long computations
    Arguments:
        n = the number of operations performed so far
        N = the total number of operations to be performed
    """
    pc = int(np.round(100*float(n)/float(N)))
    N_max = 50
    d = N//N_max + 1
    N = N//d
    n = n//d
    sys.stdout.write('\r')
    fmt = '[%%-%ds]' % N
    ostr = (fmt+' %d%%') % ('='*n,pc)
    sys.stdout.write(ostr)
    sys.stdout.flush()
    
def available(show=True):
    """List the available profiles, including those in databases
    """
    rdir = os.path.dirname(__file__)
    dbFile = os.path.join(rdir,'data','Cn2_profiles.hd5')
    store = pd.HDFStore(dbFile)
    qlist = zip(list(store['df']['Site']),list(store['df']['tile']))
    qlist += [('MK2009','25%'),('MK2009','50%'),('MK2009','75%')]
    store.close()
    qlist = map(lambda x: '%s %s'%(x[0],x[1]),qlist)
    if show:
        print '---- In-code profiles: ----'
        for p in Cn2_Profile.valid_profiles:
            print p
        print '\n---- Profiles in %s ----'%dbFile
        for q in qlist:
            print q
    else:
        return Cn2_Profile.valid_profiles+qlist

def run_cases(testmode = False, HDF=None, **kwargs):
    """This is a generic multi-loop over PSF calculations with different parameters.
    Returns a pandas DataFrame of results, along with metadata dictionary (as df.metadata).
    
    Keyword:
        HDF - the name of the HDF file to store the PSFs into. A unique ID is created and
              entered into the database in an additional column. Default: None
              
    Typical parameters, passed via kwargs, include:
        theta_set - list of constellation opening angles (arcmin)
        lam_set - list of wavelengths (microns)
        site_set - list of site names - these are used to look up Cn2 profiles in a database
    
    Other optional parameters are:
        alpha - marching out angle for field points on a line (degrees)
        radius_minimum - constrains the minimum size of a guide star constellation (arcmin)
        N - number of guidestars in the constellation
        geom - geometry of guidestar constellation ('whhel', or 'circle', with 'wheel' meaning one GS at the center)
        n - size of fine grid for the structure function calculation
    """
    # parameters to vary
    default_iters = OrderedDict(
        [
            ('theta_set', [0., 0.5, 1., 2.5, 3.5, 5.0]),
            ('lam_set',[0.55]),
            ('site_set',['MK Imaka','Armazones 25%','Armazones median','Armazones 75%',
                         'Maunakea 13N 25%','Maunakea 13N median','Maunakea 13N 75%',
                         'ORM 25%','ORM median','ORM 75%']),
        ]
    )
    # columns of the returned database:
    cols = ['Profile','telescope','DM_conjugate','wfs_conjugate','wavelength',
            'r00','r0','theta0','h_bar','constellation_radius',
            'field_angle_r','field_angle_theta','ENA_R_seeing','ENA_R','warning']
    
    if HDF is not None:
        cols = cols + ['file','date','time','uid','key']

    default_variables = [
        ('alpha',60.),
        ('radius_minimum',1.0),
        ('N',3),
        ('n',256),
        ('geom','circle'),
        ('dm_conjugate',None),
        ('wfs_conjugate',None),
        ('conjugate_dict',None),
        ('telescope',None),
        ]  # if this list is modified, change line ===>(A) below
    default_variables = OrderedDict(default_variables)
    # ------- sort out the arguments ---
    for d in [default_iters,default_variables]:
        keys = d.keys()
        dd = dict([(x,kwargs[x]) for x in keys if x in kwargs])
        d.update( dd )
    
    caseload = default_iters.keys()
    caseload = map(lambda x: default_iters[x],caseload)
    the_cases = list(itertools.product(*caseload))
    
    vns = default_variables.keys()
    
    # (A)===> change this line if default_variables is changed:
    (alpha,radius_minimum,N,n,geom,dm_conjugate,wfs_conjugate,conjugate_dict,telescope) = map(lambda x: default_variables[x],vns)
    
    telescopes = {'MK':'TMT',
                  'Maunakea':'TMT',
                  'ORM':'TMT',
                  'Armazones':'E-ELT'}
    telescope_dict = {}
    for site in default_iters['site_set']:
        key = site.split()[0]
        telescope_dict[site] = telescopes[key] if key in telescopes else ''
    
    if conjugate_dict is None:
        conjugate_dict = {'TMT':[-390]*2,
                          'E-ELT':[556]*2,
                          'Keck':[-126]*2,
                          '':[0]*2 }
    if dm_conjugate is not None:
        for key in conjugate_dict:
            conjugate_dict[key][0] = dm_conjugate
    if wfs_conjugate is not None:
        for key in conjugate_dict:
            conjugate_dict[key][1] = wfs_conjugate

    vr = np.array([np.cos(alpha*degrees),np.sin(alpha*degrees)])
    
    # open the database file
    if HDF is not None:
        dfile = h5py.File(HDF) # append or create new

    k,count = 0,len(the_cases)
    rows = []
    progress_bar(k,count)
    first = True
    
    for theta,lam,site in the_cases:
        telescope = default_variables['telescope']
        if telescope is None:
            telescope = telescope_dict[site]
        dm_conjugate, wfs_conjugate = conjugate_dict[telescope]
        radius = max(abs(theta)*1.2,radius_minimum)
        if not testmode or first:
            
            # ======== code goes here ========
            
            a = Cn2_Profile(site,lam=lam,suppressWarnings=True)
            r_lim = a.r0*n/4
            w = np.zeros(N+1)
            w[0] = -1
            w[1:] = np.ones(N)/float(N)
            radius = max(abs(theta)*1.2,radius_minimum)
            field_point = theta*vr
            constellation = Constellation(ngs=N,geometry=geom,radius=radius)
            a.make_PSF( w, constellation, n=n,
                       field_point = field_point,
                       dm_conjugate = dm_conjugate,
                       wfs_conjugate = wfs_conjugate)
            
            # ================================
            
            row = [a.name, telescope, dm_conjugate, wfs_conjugate, a.lam,
                   a.r00, a.r0,  a.theta0,  a.h_bar,   radius,
                   theta, alpha, a.PSF_seeing.ena_r,  a.PSF.ena_r, a.warning] # like to add FWHM and ellipticity
            first = False
        else:

            row = [site, telescope, dm_conjugate, wfs_conjugate, '',
                   '', '',  '',  '',   radius,
                   theta, alpha, '',  '', '']

        uid,dat,tim = uniq_id(5)
        key = '%s_%sT%s'%(uid,dat,tim)
        if HDF is not None:
            grp = dfile.create_group(key)
            grp.create_dataset('data',data=a.PSF)
            attrs = a.PSF.__dict__
            grp.create_dataset('attrs',data=json.dumps(attrs))
            row = row + [HDF,dat,tim,uid,key]
            hdr = dict(pd.Series(row,cols))
            grp.create_dataset('header',data = json.dumps(hdr))
        rows.append(row)
        k += 1
        progress_bar(k,count)
    
    progress_bar(count,count)
    print '\nDone'
    df = pd.DataFrame(rows,columns = cols)
    df.metadata = {
        'code':'paper2.run_cases',
        'iters':default_iters, 'variables':default_variables,
        'time':time.strftime('%Y/%m/%dT%H:%M:%S')
    }
    
    if HDF is not None:
        dfile.close()
    
    return df

def uniq_id(n):
    """Create a unique id string ('key') containing n random characters
    followed by a timestamp.
    
    Returns the random character string, the datestamp, and the timestamp
    as a tuple of strings
    """
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    uid = ''.join(random.choice(chars) for _ in range(n))
    dat,tim = str(pd.Timestamp('now')).split(' ')
    return uid,dat,tim
    
def dfSave(df,name,hfile = 'paper3.h5'):
    """Save a pandas database in an HDF file.
    This will also save the metadata.
    It will not overwrite existing datasets in the HDF file, unless told to.
    
    Argument:
        df - the pandas dataset
        name - the name to give it in the HDF Store file
    """
    store = pd.HDFStore(hfile)
    if name not in store:
        store[name] = df
        if hasattr(df,'metadata'):
            store.get_storer(name).attrs.metadata = metadata
    else:
        print 'WARNING - %s is in %s. opted not to write over'%(name,hfile)
    store.close()
    
def dfRead(name,hfile='paper3.h5'):
    """Read a pandas database from an HDF file.
    """
    store = pd.HDFStore(hfile)
    df = store[name]
    q = store.get_storer(name)
    if hasattr(q,'metadata'):
        df.metadata = q.metadata
    store.close
    return df

def oft(A):
    """Optical Fourier Transform
    """
    return np.abs( np.fft.ifftshift( np.fft.fft2( np.fft.fftshift(A))))

def dict_filter(dict,key_list):
    """Return a dictionary derived from dict but having only keys from key_list
    """
    r = {}
    for key in dict:
        if key in key_list:
            r[key] = dict[key]
    return r

def fwhm(f):
    """determine full-width-half-max of a lineout
    """
    k = np.argmax(f)
    x = f.max()
    u = np.abs(f[0:k]-0.5*x)
    k1 = np.argmin(u)
    u = np.abs(f[k:]-0.5*x)
    k2 = np.argmin(u)+k
    return k2-k1

def fwhm2(f,method='area'):
    """find the full-width-half-maxima of a 2d blob
    """
    n,m = f.shape
    fmax = f.max()
    b = (f > fmax/2).astype(int)
    if method == 'area':
        cb = b.sum()
        r = np.sqrt(cb/np.pi)*2.
        r_major,r_minor = r,r
    if method == 'slice':
        return (fwhm(f[n/2,:]),fwhm(f[:,m/2]))
    else:
        iy,ix = np.where(f > fmax/2.)
        cx = np.average(ix.astype(float))
        cy = np.average(iy.astype(float))
        x = ix - cx
        y = iy - cy
        r = np.sqrt(x**2+y**2)
        k = np.argmax(r)
        theta = np.arctan2(x[k],y[k])
        rp = np.arange(0,r.max())
        xp,yp = rp*np.cos(theta+np.pi/2),rp*np.sin(theta+np.pi/2)
        ixp,iyp = (xp+cx).astype(int),(yp+cy).astype(int)
        c = b.flat[ixp+iyp*n]
        xp,yp = xp[np.where(c)],yp[np.where(c)]
        rp = np.sqrt(xp**2+yp**2)
        r_major = r.max()
        r_minor = rp.max()
    return (2*r_major,2*r_minor)

# --------------------------- Tests -------------------------------------

def test():
    df = run_cases(testmode=True)
    print df
