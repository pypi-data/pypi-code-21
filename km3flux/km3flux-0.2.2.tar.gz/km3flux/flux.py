"""Assorted Fluxes, in  (m^2 sec sr GeV)^-1"""

import logging
from six import string_types

import h5py
import numpy as np
import pandas as pd
from scipy.integrate import romberg, simps
from scipy.interpolate import splrep, splev, RectBivariateSpline

from km3pipe.mc import name2pdg, pdg2name
from km3flux.data import (HONDAFILE, dm_gc_spectrum, dm_sun_spectrum,
                          DM_GC_FLAVORS, DM_GC_CHANNELS, DM_GC_MASSES,
                          # DM_SUN_FLAVORS, DM_SUN_CHANNELS, DM_SUN_MASSES
                         )
from km3pipe.tools import issorted, bincenters

FLAVORS = ('nu_e', 'anu_e', 'nu_mu', 'anu_mu')
MCTYPES = [name2pdg(name) for name in FLAVORS]

logger = logging.getLogger(__name__)


class BaseFlux(object):
    """Base class for fluxes.

    Methods
    =======
    __call__(energy, zenith=None)
        Return the flux on energy, optionally on zenith.
    integrate(zenith=None, emin=1, emax=100, **integargs)
        Integrate the flux via romberg integration.
    integrate_samples(energy, zenith=None, emin=1, emax=100)
        Integrate the flux from given samples, via simpson integration.

    Example
    =======
    >>> zen = np.linspace(0, np.pi, 5)
    >>> ene = np.logspace(0, 2, 5)

    >>> from km3flux.flux import MyFlux
    >>> flux = MyFlux(flavor='nu_mu')

    >>> flux(ene)
    array([6.68440000e+01, 1.83370000e+01, 4.96390000e+00,
           1.61780000e+00, 5.05350000e-01,])
    >>> flux(ene, zen)
    array([2.29920000e-01, 2.34160000e-02, 2.99460000e-03,
           3.77690000e-04, 6.87310000e-05])
    """
    def __init__(self, **kwargs):
        pass

    def __call__(self, energy, zenith=None, interpolate=True):
        logger.debug("Interpolate? {}".format(interpolate))
        energy = np.atleast_1d(energy)
        logger.debug("Entering __call__...")
        if zenith is None:
            logger.debug("Zenith is none, using averaged table...")
            return self._averaged(energy, interpolate=interpolate)
        zenith = np.atleast_1d(zenith)
        if len(zenith) != len(energy):
            raise ValueError("Zenith and energy need to have the same length.")
        logger.debug("Zenith available, using angle-dependent table...")
        return self._with_zenith(energy=energy, zenith=zenith,
                                 interpolate=interpolate)

    def _averaged(self, energy, interpolate=True):
        logger.debug("Interpolate? {}".format(interpolate))
        raise NotImplementedError

    def _with_zenith(self, energy, zenith, interpolate=True):
        logger.debug("Interpolate? {}".format(interpolate))
        raise NotImplementedError

    def integrate(self, zenith=None, emin=1, emax=100, interpolate=True, **integargs):
        logger.debug("Interpolate? {}".format(interpolate))
        return romberg(self, emin, emax, vec_func=True, **integargs)

    def integrate_samples(self, energy, zenith=None, emin=1, emax=100,
                          interpolate=True, **integargs):
        logger.debug("Interpolate? {}".format(interpolate))
        energy = np.atleast_1d(energy)
        mask = (emin <= energy) & (energy <= emax)
        energy = energy[mask]
        if zenith:
            logger.debug("Zenith available, using angle-dependent table...")
            zenith = np.atleast_1d(zenith)
            zenith = zenith[mask]
        flux = self(energy, zenith=zenith, interpolate=interpolate)
        return simps(flux, energy, **integargs)


class PowerlawFlux(BaseFlux):
    """E^-gamma flux."""
    def __init__(self, gamma=2, scale=1e-4):
        self.gamma = gamma
        self.scale = scale

    def _averaged(self, energy, interpolate=True):
        return self.scale * np.power(energy, -1 * self.gamma)

    def integrate(self, zenith=None, emin=1, emax=100, **integargs):
        """Compute analytic integral instead of numeric one."""
        if np.around(self.gamma, decimals=1) == 1.0:
            return np.log(emax) - np.log(emin)
        num = np.power(emax, 1 - self.gamma) - np.power(emin, 1 - self.gamma)
        den = 1.0 - self.gamma
        return self.scale * (num / den)


class Honda2015(BaseFlux):
    """
    Get Honda 2015 atmospheric neutrino fluxes.

    Whitepaper at https://arxiv.org/abs/1502.03916.

    Flux table downloaded from http://www.icrr.u-tokyo.ac.jp/~mhonda/

    Flux at Frejus site, no mountain, solar minimum.

    Methods
    =======
    __init__(flavor='nu_mu')
        Load flux table for the given neutrino flavor.
    __call__(energy, zenith=None)
        Return the flux on energy, optionally on zenith.
    integrate(zenith=None, emin=1, emax=100, **integargs)
        Integrate the flux via omberg integration.
    integrate_samples(energy, zenith=None, emin=1, emax=100)
        Integrate the flux from given samples, via simpson integration.
    """
    def __init__(self, flavor='nu_mu'):
        self.table = None
        self.avtable = None
        filename = HONDAFILE
        if flavor not in FLAVORS:
            raise ValueError("Unsupported flux '{}'".format(flavor))
        with h5py.File(filename, 'r') as h5:
            self.energy_bins = h5['energy_binlims'][:]
            self.cos_zen_bins = h5['cos_zen_binlims'][:]
            self.table = h5[flavor][:]
            self.avtable = h5['averaged/' + flavor][:]
        # adjust upper bin for the case zenith==0
        self.cos_zen_bins[-1] += 0.00001
        self.energy_bincenters = bincenters(self.energy_bins)
        self.cos_zen_bincenters = bincenters(self.cos_zen_bins)
        assert issorted(self.cos_zen_bincenters)
        assert issorted(self.energy_bincenters)
        assert self.avtable.shape == self.energy_bincenters.shape
        assert self.table.shape[0] == self.cos_zen_bincenters.shape[0]
        assert self.table.shape[1] == self.energy_bincenters.shape[0]
        self.avinterpol = splrep(
            self.energy_bincenters,
            self.avtable,
        )
        self.interpol = RectBivariateSpline(
            self.cos_zen_bincenters,
            self.energy_bincenters,
            self.table
        )

    def _averaged(self, energy, interpolate=True):
        logger.debug("Interpolate? {}".format(interpolate))
        if not interpolate:
            fluxtable = self.avtable
            ene_bin = np.digitize(energy, self.energy_bins)
            ene_bin = ene_bin - 1
            return fluxtable[ene_bin]
        else:
            flux = splev(energy, self.avinterpol)
            return flux

    def _with_zenith(self, energy, zenith, interpolate=True):
        logger.debug("Interpolate? {}".format(interpolate))
        energy = np.atleast_1d(energy)
        zenith = np.atleast_1d(zenith)
        cos_zen = np.cos(zenith)
        if not interpolate:
            fluxtable = self.table
            ene_bin = np.digitize(energy, self.energy_bins)
            zen_bin = np.digitize(cos_zen, self.cos_zen_bins)
            ene_bin = ene_bin - 1
            zen_bin = zen_bin - 1
            return fluxtable[zen_bin, ene_bin]
        else:
            flux = self.interpol.ev(cos_zen, energy)
            return flux


class HondaSarcevic(BaseFlux):
    """
    Get Honda + Sarcevic atmospheric neutrino fluxes.
    """
    def __init__(self, flavor='nu_mu'):
        self.table = None
        self.avtable = None
        filename = HONDAFILE
        if flavor not in FLAVORS:
            raise ValueError("Unsupported flux '{}'".format(flavor))
        with h5py.File(filename, 'r') as h5:
            self.energy_bins = h5['energy_binlims'][:]
            self.cos_zen_bins = h5['cos_zen_binlims'][:]
            self.table = h5['honda_sarcevic/' + flavor][:]
        # adjust upper bin for the case zenith==0
        self.cos_zen_bins[-1] += 0.00001

    def _averaged(self, energy, interpolate=True):
        raise NotImplementedError("Supports only zenith dependent flux!")

    def _with_zenith(self, energy, zenith, interpolate=True):
        fluxtable = self.table
        cos_zen = np.cos(zenith)
        ene_bin = np.digitize(energy, self.energy_bins)
        zen_bin = np.digitize(cos_zen, self.cos_zen_bins)
        ene_bin = ene_bin - 1
        zen_bin = zen_bin - 1
        return fluxtable[zen_bin, ene_bin]


class DarkMatterFlux(BaseFlux):
    """
    Get Dark Matter WimpWimp->foo->nu spectra.

    Curently only gives Galactic Center spectra (taken from M. Cirelli).

    Methods
    =======
    __init__(source='gc', flavor='nu_mu', channel='w', mass=1000)
        Load flux table for the given neutrino flavor.
    __call__(energy, zenith=None, interpolate=True)
        Return the flux on energy, optionally on zenith.
    integrate(zenith=None, emin=1, emax=100, **integargs)
        Integrate the flux via romberg integration.
    integrate_samples(energy, zenith=None, emin=1, emax=100)
        Integrate the flux from given samples, via simpson integration.

    Example
    =======
    >>> from km3flux import DarkMatterFlux
    >>> print(DarkMatterFlux.flavors)
    >>> flux = DarkMatterFlux(flavor='anu_mu', channel='w', mass=1000)
    >>> ene = np.geomspace(1, 100, 11)
    >>> print(flux(ene, interpolate=True))
    """
    flavors = DM_GC_FLAVORS
    channels = DM_GC_CHANNELS
    masses = DM_GC_MASSES

    def __init__(self, source='gc', flavor='nu_mu', channel='w', mass=1000):
        """
        Parameters
        ==========
        source: string, optional [default: 'gc']
            Object where the WimpWimp annihilates. Currently only 'gc'
        flavor: string, optional [default: 'nu_mu']
            Neutrino flavor. See available flavors stored in
            ``DarkMatterFlux.flavors``
        channel: string, optional [default: 'w']
            WimpWimp annihilation channel (WimpWimp -> foofoo).
            See available channels stored in ``DarkMatterFlux.channels``
        mass: int, optional [default: 1000]
            WimpWimp parent mass.
            See available masses stored in ``DarkMatterFlux.masses``
        """
        self.flavor = flavor
        self.channel = channel
        self.mass = mass
        if source == 'sun':
            loader = dm_sun_spectrum
        else:
            loader = dm_gc_spectrum

        self.avtable, self.energy_bins = loader(flavor=flavor, channel=channel,
                                                mass=mass, full_lims=True)
        self.energy_bincenters = bincenters(self.energy_bins)
        self.avinterpol = splrep(
            self.energy_bincenters,
            self.avtable,
        )

    def _averaged(self, energy, interpolate=True):
        logger.debug("Interpolate? {}".format(interpolate))
        energy = np.atleast_1d(energy)
        if np.any(energy > self.energy_bins.max()):
            raise ValueError(
                "Some energies exceed parent mass '{}'!".format(self.mass))
        if not interpolate:
            fluxtable = self.avtable
            ene_bin = np.digitize(energy, self.energy_bins)
            ene_bin = ene_bin - 1
            return fluxtable[ene_bin]
        else:
            flux = splev(energy, self.avinterpol)
            return flux

    def _with_zenith(self, energy, zenith, interpolate=True):
        logger.debug("Interpolate? {}".format(interpolate))
        logging.warning('No zenith dependent flux implemented! '
                        'Falling back to averaged flux.'
                       )
        return self._averaged(self, energy)


class AllFlavorFlux():
    """Get mixed-flavor fluxes.

    Methods
    =======
    __init__(fluxclass='Honda2015')

    __call__(energy, zenith=None, interpolate=True)
        Return the flux on energy, optionally on zenith.
    """
    fluxmodels = {
        'Honda2015': Honda2015,
        'HondaSarcevic': HondaSarcevic,
    }

    def __init__(self, fluxclass='Honda2015'):
        if isinstance(fluxclass, string_types):
            fluxclass = self.fluxmodels[fluxclass]
        self.flux_flavors = {}
        for flav in FLAVORS:
            self.flux_flavors[flav] = fluxclass(flav)

    def __call__(self, energy, zenith=None, flavor=None, mctype=None,
                 interpolate=True):
        """mctype is ignored if flavor is passed as arg."""
        if mctype is None and flavor is None:
            raise ValueError("Specify either mctype(int) or flavor(string)")
        if flavor is None:
            mctype = pd.Series(np.atleast_1d(mctype))
            flavor = mctype.apply(pdg2name)
        flavor = np.atleast_1d(flavor)
        energy = np.atleast_1d(energy)
        out = np.zeros_like(energy)
        if zenith is not None:
            zenith = np.atleast_1d(zenith)
        for flav in np.unique(flavor):
            where = flavor == flav
            if zenith is not None:
                loczen = zenith[where]
            flux = self.flux_flavors[flav](energy[where], loczen,
                                           interpolate=interpolate)
            out[where] = flux
        return out
