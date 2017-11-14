""" Geometrical optics (optical path length)
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
import scipy.special as sps

from ..common_methods import average_radial
from ..common_variables import types_indexable


def sphere(
    radius=5,
    n_object=1.339,
    n_medium=1.333,
    distance=0,
    extent=20,
    wavelength=5,
    offset_x=0,
    offset_y=0,
    interpolate=3,
    average=False
):
    """
    Computes the optical path length through a dielectric sphere.

    Parameters
    ----------
    radius : float
        Radius of the cylinder in vacuum wavelengths.
    n_object : float
        Refractive index of the cylinder.
    n_medium : float
        Refractive index of the surrounding medium.
    distance : float
        Distance lD from the detector to the center of the cylinder
        in vacuum wavelengths. If `distance<radius`, the field will be
        automatically refocused to match the behavior of a microscope.
        Does not have any effect here
    extent : float or tuple
        Size of detector in wavelengths. If a float is given, then the
        detector will have a square shape. A tuple is interpreted as the
        rectangular (x,y) size of the detector. 
    wavelength : float
        Resolution of detector in pixels per vacuum wavelength.
    offset_x : float
        Offset in x direction in vacuum wavelengths
    offset_y : float
        Offset in y direction in vacuum wavelengths
    interpolate : int
        If not zero: Instead of computing the entire field, only compute
        the radial field with a sampling that is by a factor of `interpolate`
        higher than the required data and interpolate the 2D field from there.
        This is faster than computing the redundant full field (`interpolate=0`).

    Returns
    -------
    field : 2d ndarray
        The scattered, background corrected field
    """
    if isinstance(extent, types_indexable):
        x = np.linspace(-extent[0] / 2, extent[0] / 2,
                        int(np.round(wavelength * extent[0])), endpoint=True)
        y = np.linspace(-extent[1] / 2, extent[1] / 2,
                        int(np.round(wavelength * extent[1])), endpoint=True)
        cx, cy = np.meshgrid(x, y)
    else:
        x = np.linspace(-extent / 2, extent / 2,
                        int(np.round(wavelength * extent)))
        cy, cx = np.meshgrid(x, x)

    cx += offset_x
    cy += offset_y

    z = np.zeros_like(cx)
    radcoord = radius**2 - cx**2 - cy**2
    radcoordg0 = radcoord > 0
    z[radcoordg0] = 2 * np.sqrt(radcoord[radcoordg0])

    # dn is normalized to one wavelength
    dn = (n_object - n_medium) * z

    if average:
        dn = average_radial(dn, center=(
            offset_x * wavelength, offset_y * wavelength))

    return np.exp(1j * 2 * np.pi * dn).transpose()


def sphere_radial(
    radius=5,
    n_object=1.339,
    n_medium=1.333,
    distance=0,
    radial_extent=20,
    wavelength=5,
    oversample=4,
    average=False
):
    """ Compute radial projection of sphere in a very complicated way

    Parameters
    ----------
    radius : float
        Radius of the cylinder in vacuum wavelengths.
    n_object : float
        Refractive index of the cylinder.
    n_medium : float
        Refractive index of the surrounding medium.
    distance : float
        Distance lD from the detector to the center of the cylinder
        in vacuum wavelengths. If `distance<radius`, the field will be
        automatically refocused to match the behavior of a microscope.
    radial_extent : float or tuple
        Radial size of detector in wavelengths.
    wavelength : float
        Resolution of detector in pixels per vacuum wavelength.
    oversample : int
        Oversampling (zero-padding) to prevent offset in results

    Returns
    -------
    field : 1d ndarray
        The scattered, background corrected radial field
    """
    size = radial_extent * wavelength
    assert int(size) == size
    r = np.linspace(0, radial_extent, size, endpoint=True)
    y = np.zeros_like(r)
    where_disc = r <= radius
    obj2phase = (n_object - n_medium) * 2 * np.pi
    y[where_disc] = 2 * np.sqrt(radius**2 - r[where_disc]**2) * obj2phase

    return np.exp(1j * y)
