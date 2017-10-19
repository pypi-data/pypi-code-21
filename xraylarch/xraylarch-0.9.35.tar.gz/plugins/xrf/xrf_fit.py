#!/usr/bin/env python
"""
provide xrf_model() and xrf_fit() functions
to create an XRF model and fit a spectrum to this model

"""

import numpy as np
from scipy.interpolate import UnivariateSpline
from larch import (Group, Parameter, isParameter,
                   ValidateLarchPlugin,
                   param_value, isNamedClass)

from larch_plugins.xray import (xray_edge, xray_lines,
                                atomic_density, mu_elam,
                                material_mu)

from larch_plugins.math import gaussian, lorentzian, voigt, pvoigt


def detector_efficiency(energy, material, thickness):
    """return detector absorption efficiency
    Parameters
    ----------
    energy     array of energies in eV
    material   detecting element (solid state)
    thickness  detector thickness in cm

    returns array of detection efficiency
    """
    density = atomic_density(material)
    mu = mu_elam(material, energy, 'photo')
    return 1.0 - exp(mu * density * thickness)


def filter_attenuation(energy, material, thickness, density=None):
    """return attenuation factor for a given filter,
    defined by material formula, thickness (in millimeters),
    and optionally density (if not known)

    Parameters
    ----------
    energy    array of energies in eV
    material  filter material
    thickness filter thickness in cm
    density   filter density (g/cm^3) or None to use default,
              known density for material

    returns array of attenuation factor

    """
    mu = material_mu(material, energy, density=density)
    return exp(-mu * thickness)


class ElementPeak(Group):
    """hold all XRF peaks for an element within an energy range
    """

    def __init__(self, elem, amplitude=1000, excitation_energy=50000.,
                 min_energy=1000.0, fano_factor=0.4, _larch=None, **kws):

        self._larch = _larch
        self.elem = elem
        self.amplitude = amplitude
        self.excitation_energy = excitation_energy
        self.min_energy = min_energy
        self.fano_factor = fano_factor
        self.params = {}
        self.lines = []
        if elem is not None:
            self.add_lines()
                enmin=self.enmin, enmax=self.enmax)

    def add_lines(self, excitation_energy=None, min_energy=None):
        if excitation_energy is None:
            excitation_energy = self.excitation_energy
        if min_energy is None:
            min_energy = self.min_energy

        selem = self.elem.title()
        params["%s_amp" % selem] = Parameter(self.amplitude, min=0, vary=True)

        all_lines = xray_lines(self.elem, excitation_energy=excitation_energy)
        edges = xray_edges(self.elem)

        for lname, dat in all_lines.items():
            line_energy, shell_amp, init_level, final_level = dat
            edge_energy, fyield, jump = edges[init_level]

            name = '%s_%s' % (elem, lname)
            self.lines.append(name)
            sig_expr = 'sqrt(noise**2 + %.5f)' % (self.fano_factor*line_energy)

            self.params['%s_cen' % name] = Parameter(value=line_energy vary=False)
            self.params['%s_amp' % name] = Parameter(expr='%s_amp*%f' % (selem, shell_amp)))
            self.params['%s_sig' % name] = Parameter(expr=sig_expr))






class XRFFitter(Group):
    def __init__(self, name=None, _larch=None, **kws):
        self._larch = _larch
        kwargs = {'name': name}
        kwargs.update(kws)




@ValidateLarchPlugin
def xrf_fit(datagroup, fitter, larch=None, **kws):
    """fit an XRF Fit for an MCA dataset and an XRF fitting model

    Parameters:
    -----------
      name:  name of peak -- may be used for auto-setting center
             'Fe Ka1',  'Pb Lb1', etc
      amplitude:
      center:
      sigma:
      shape   peak shape (gaussian, voigt, lorentzian)

    For all the options described as **value or parameter** either a
    numerical value or a Parameter (as created by param()) can be given.

    Returns:
    ---------
        an XRFPeak Group.

    """
    return XRFPeak(name=name, amplitude=amplitude, sigma=sigma, center=center,
                    shape=shape, sigma_params=sigma_params, _larch=_larch)

def registerLarchPlugin():
    return ('_xrf', {'xrf_peak': xrf_peak})
