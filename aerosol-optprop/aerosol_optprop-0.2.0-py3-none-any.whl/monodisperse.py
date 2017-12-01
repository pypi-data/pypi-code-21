import miepython as mie
import numpy as np
from aerosol_optprop.util import CrossSection
from typing import Tuple
import os


class Monodisperse:

    def __init__(self, radius, n=1):

        # distribution parameters
        self._radius = radius
        self._n = n

        # storage of extinction if it is set by user
        self.persistent_extinction = True
        self._k = None
        self._k_wavelength = None

        # in the future we could cache cross section, phase functions, etc at a particular wavelength
        self._wavelength = None
        self._has_changed = True

        # where to lookup the refractive indices
        self.refractive_index_file = 'refractive_index'

    @property
    def n(self):
        return self._n

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._has_changed = True
        # maintain extinction if n is set through k
        if self._k is not None and self.persistent_extinction:
            old_xsec = self.cross_section(self._k_wavelength).extinction
            self._radius = value
            new_xsec = self.cross_section(self._k_wavelength).extinction
            self._n = self._n * old_xsec / new_xsec
        else:
            self._radius = value

    @property
    def surface_area_density(self):
        return 4 * np.pi * self.n * self.radius**2

    @property
    def volume_density(self):
        return 4 / 3 * np.pi * self.n * self.radius**3

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
        r = self.radius
        x = 2 * np.pi * self.radius / wavelength
        m = self.refractive_index(wavelength)

        qext, qsca, qback, g = mie.mie(m, x)
        qqsca = qsca * np.pi * r ** 2
        qqext = qext * np.pi * r ** 2

        return CrossSection(scattering=qqsca * (1e-4 ** 2),
                            extinction=qqext * (1e-4 ** 2),
                            absorption=(qqext - qqsca) * (1e-4 ** 2))

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
        r = self.radius
        x = 2 * np.pi * r / wavelength
        mu = np.cos(scattering_angles * np.pi / 180)
        m = self.refractive_index(wavelength)

        _, qqsca, _, _ = mie.mie(m, x)
        qqsca *= np.pi * r**2

        if x < 0.1:
            if np.real(m) == 0:
                s1, s2 = mie.small_mie_conducting_S1_S2(m, x, mu)
            else:
                s1, s2 = mie.small_mie_S1_S2(m, x, mu)
        else:
            s1, s2 = mie.mie_S1_S2(m, x, mu)

        return (np.abs(s1) ** 2 + np.abs(s2) ** 2) * 2 * np.pi
