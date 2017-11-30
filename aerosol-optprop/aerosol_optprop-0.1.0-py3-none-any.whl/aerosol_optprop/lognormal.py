import miepython as mie
import numpy as np
from collections import namedtuple
from typing import Tuple
import os

CrossSection = namedtuple('CrossSection', ['scattering', 'extinction', 'absorption'])


class AerosolLognormal:

    def __init__(self, median_radius: float=0.08, width: float=1.6, n: float=1.0):
        """
        Class to handle the optical property calculations of a lognormal distribution of spherical sulphate particles.
        Radii and wavelength parameters are in units of microns.

        The equation describing the distribution is:

        .. math::
            dn/dr = n/(\sqrt{2\pi}r\sigma_g)\exp(-(\ln(r)-\ln(r_g))^2/2\sigma_g^2)

        where :math:`r_g` is median radius, and :math:`\sigma_g` is the width. The code uses the
        `miepython <https://github.com/scottprahl/miepython>`_ implementation of the Wiscombe code developed by
        Scott Prahl for Mie calculations.

        A simple example::

            from aerosol_optprop import AerosolLognormal

            # create a lognormal distribution and compute the cross section
            aerosol = AerosolLognormal(median_radius=0.1, width=1.5)
            aerosol.cross_section(wavelength=0.525)

            # update the particle number density using a fixed extinction
            aerosol.set_n_from_extinction(extinction=1e-3, wavelength=0.525, persistant=True)
            aerosol.n

            # calculate derived parameters
            aerosol.surface_area_density
            aerosol.mode_radius = 0.1  # set the mode radius of the distribution
            aerosol.median_radius  # median radius has been automatically updated
            aerosol.extinction(wavelength=0.525)  # extinction is unchanged
            aerosol.n  # number density has been updated

        Parameters
        ----------
            median_radius: median radius of the distributin in microns
            width: width parameter of the distributin
            n: (optional) aerosol number density, default is 1
        """

        # distribution variables
        self._median_radius = median_radius
        self._width = width
        self._n = n

        # storage of extinction if it is set by user
        self._k = None
        self._k_wavelength = None
        self.persistent_extinction = True

        # sampling at which to perform quadrature
        self.num_sigma = 7
        self.num_samples = 50

        # linearly or logarithmically space the quadrature points
        self.logspace = False

        # where to lookup the refractive indices
        self.refractive_index_file = 'refractive_index'

        # in the future we could cache cross section, phase functions, etc at a particular wavelength
        self._wavelength = None
        self._has_changed = True

    @property
    def median_radius(self):
        return self._median_radius

    @median_radius.setter
    def median_radius(self, value):
        self._has_changed = True
        # maintain extinction if n is set through k
        if self._k is not None and self.persistent_extinction:
            old_xsec = self.cross_section(self._k_wavelength).extinction
            self._median_radius = value
            new_xsec = self.cross_section(self._k_wavelength).extinction
            self._n = self._n * old_xsec / new_xsec
        else:
            self._median_radius = value

    @property
    def width(self):

        return self._width

    @width.setter
    def width(self, value):
        self._has_changed = True
        # maintain extinction if n is set through k
        if self._k is not None and self.persistent_extinction:
            old_xsec = self.cross_section(self._k_wavelength).extinction
            self._width = value
            new_xsec = self.cross_section(self._k_wavelength).extinction
            self._n = self._n * old_xsec / new_xsec
        else:
            self._width = value

    @property
    def n(self):
        return self._n

    @property
    def mode_radius(self):
        return self.median_radius * np.exp(-np.log(self.width)**2)

    @mode_radius.setter
    def mode_radius(self, value):
        self.median_radius = value * np.exp(np.log(self.width)**2)

    @property
    def surface_area_density(self):
        return 4 * np.pi * self.n * np.exp(2 * np.log(self.median_radius) + 2 * np.log(self.width) ** 2)

    @property
    def volume_density(self):
        return 4 / 3 * np.pi * self.n * np.exp(3 * np.log(self.median_radius) + 9 / 2 * np.log(self.width) ** 2)

    @property
    def radii(self):
        num = self.num_sigma * 2 * self.num_samples
        if self.logspace:
            return np.logspace((np.log(self.mode_radius) - self.num_sigma * np.log(self.width)) / np.log(10),
                               (np.log(self.mode_radius) + self.num_sigma * np.log(self.width)) / np.log(10), num)
        else:
            return np.linspace(np.exp(np.log(self.mode_radius) - self.num_sigma * np.log(self.width)),
                               np.exp(np.log(self.mode_radius) + self.num_sigma * np.log(self.width)), num)

    def set_n_from_extinction(self, extinction: float, wavelength: float, persistant: bool=True):
        """
        Set the aerosol number density from the extinction

        Parameters
        ----------
            extinction: extinction in units of km^-1
            wavelength: wavelength in microns
            persistant: (optional) If true the extinction is maintained at a constant value even if size parameters
                are changed. Default=True
        """
        self.persistent_extinction = persistant
        self._k = extinction
        self._k_wavelength = wavelength
        self._n = extinction * 1e-5 / self.cross_section(wavelength).extinction

    def pdf(self, radii: np.ndarray=None):
        """
        Return the lognormal distribution function

        Parameters
        ----------
            radii: (optional) array of radii in microns that the number density will be returned at.
                Defaults to the quadrature points
        """
        if radii is None:
            radii = self.radii

        return 1 / (np.sqrt(2 * np.pi) * radii * np.log(self.width)) * np.exp(
            -(np.log(radii / self.median_radius) ** 2) / (2 * np.log(self.width) ** 2))

    def angstrom_coefficient(self, wavelengths: Tuple[float, float]) -> float:
        """
        Return the angstrom coefficient between two wavelengths

        Parameters
        ----------
        wavelengths: (float, float) wavelength pair in microns

        Returns
        -------
        angstrom_coefficient: (float)
        """
        return np.log(self.cross_section(wavelengths[1]).scattering / self.cross_section(wavelengths[0]).scattering) / \
               np.log(wavelengths[1] / wavelengths[0])

    def extinction(self, wavelength: float) -> float:
        """
        Calculate the aerosol extinction in units of per km

        Parameters
        ----------
            wavelength: (float) wavelength in microns

        Returns
        -------
            extinction: (float)
        """
        return self.cross_section(wavelength).extinction * self.n * 1e5

    def cross_section(self, wavelength: float) -> CrossSection:
        """
        Calcualate the scattering, extinction and absorption cross sections of the aerosol distribution

        Parameters
        ----------
            wavelength: wavelength in microns to compute the cross sections at

        Returns
        -------
            cross sections: named tuple containing 'scattering' 'extinction' and 'absorption' values
        """
        r = self.radii
        x = 2 * np.pi * r / wavelength
        n = self.pdf(r)

        qqsca = np.zeros(len(x))
        qqext = np.zeros(len(x))
        m = self.refractive_index(wavelength)

        for i in range(len(x)):
            qext, qsca, qback, g = mie.mie(m, x[i])
            qqsca[i] = qsca * np.pi * r[i] ** 2
            qqext[i] = qext * np.pi * r[i] ** 2

        return CrossSection(scattering=np.trapz(qqsca * n, r) * (1e-4 ** 2),
                            extinction=np.trapz(qqext * n, r) * (1e-4 ** 2),
                            absorption=np.trapz((qqext - qqsca) * n, r) * (1e-4 ** 2))

    def asymmetry_factor(self, wavelength: float) -> float:
        """
        Calculate the assymetry factor, defined as

        .. math::
            g = \int_{4\pi} P(\Theta)\cos(\Theta)d\Omega

        Parameters
        ----------
            wavelength: (float) wavelength in microns

        Returns
        -------
            assymetry_factor: (float)
        """
        r = self.radii
        x = 2 * np.pi * r / wavelength
        n = self.pdf(r)

        asymm = np.zeros(len(x))
        qqsca = np.zeros(len(x))
        m = self.refractive_index(wavelength)

        for i in range(len(x)):
            _, qsca, _, asymm[i] = mie.mie(m, x[i])
            qqsca[i] = qsca * np.pi * r[i] ** 2

        return np.trapz(asymm * n * qqsca, r) / np.trapz(n * qqsca, r)

    def phase_function(self, wavelength: float, scattering_angles: np.ndarray=np.arange(0, 181)) -> np.ndarray:
        """
        Return the scattering phase function, normalized such that

        .. math::
            \int_{4\pi} P(\Theta)d\Omega = 4\pi

        Parameters
        ----------
            wavelength: (float) wavelength in microns
            scattering_angles: (optional, np.ndarray) angles in degrees at which to compute the phase function.
                Default is 0..180 in 1 degree steps

        Returns
        -------
            phase_function: np.ndarray
        """
        r = self.radii
        n = self.pdf(r)
        x = 2 * np.pi * r / wavelength
        mu = np.cos(scattering_angles * np.pi / 180)
        p = np.zeros((len(x), len(scattering_angles)))
        qqsca = np.zeros(len(x))

        m = self.refractive_index(wavelength)
        for idx, (xi, ri) in enumerate(zip(x, r)):
            _, qqsca[idx], _, _ = mie.mie(m, xi)
            qqsca[idx] *= np.pi * ri**2
            if xi < 0.1:
                if np.real(m) == 0:
                    s1, s2 = mie.small_mie_conducting_S1_S2(m, xi, mu)
                else:
                    s1, s2 = mie.small_mie_S1_S2(m, xi, mu)
            else:
                s1, s2 = mie.mie_S1_S2(m, xi, mu)

            p[idx] = (np.abs(s1) ** 2 + np.abs(s2) ** 2) * 2 * np.pi

        return np.trapz(p * (n * qqsca)[:, np.newaxis], r, axis=0) / np.trapz(n * qqsca, r)

    def single_scatter_albedo(self, wavelength: float) -> float:
        """
        Compute the single scatter albedo - the ratio of scattering to total extinction

        Parameters
        ----------
            wavelength: wavelength in microns

        Returns
        -------
            single_scatter_albedo: (float)
        """
        xsec = self.cross_section(wavelength)
        return xsec.scattering / xsec.extinction

    def refractive_index(self, wavelength: np.ndarray) -> np.ndarray:
        """
        Get the refractive index of sulphate aerosols (75%H2SO4/25%H2O) at the specified wavelength.
        See the `self.refractive_index_file` file for more details on the data

        Parameters
        ----------
            wavelength: wavelength in microns. Can be an array or a float

        Returns
        -------
            refractive index: complex refractive index
        """
        if not hasattr(wavelength, '__len__'):
            return_float = True
            wavelength = np.array([wavelength])
        else:
            return_float = False

        mu = 1e4 / np.array(wavelength)
        data = np.loadtxt(os.path.join(os.path.dirname(__file__), '..', 'data', self.refractive_index_file))
        n = np.interp(mu, data[:, 0], data[:, 1])
        k = np.interp(mu, data[:, 0], data[:, 2])

        if return_float:
            return n[0]-k[0]*1j

        return n - k * 1j
