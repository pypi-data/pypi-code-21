"""Plotting utilities.
"""
import matplotlib.pyplot as plt

from astropy.units import degree


def ra_dec(skycoord):
    """Take (ra, dec) from skycoord in matplotlib-firendly format.

    This wraps the ra because astropy's convention differs from matplotlib.
    """
    ra = skycoord.ra.wrap_at(180 * degree).radian
    dec = skycoord.dec.radian
    return ra, dec


def projection_axes(projection='aitoff', **figargs):
    fig = plt.figure(**figargs)
    ax = fig.add_subplot(111, projection=projection)
    ax.grid(color='lightgrey')
    return ax


def plot_equatorial(evts, projection='aitoff',
                    ax=None, marker='o', markersize=4,
                    alpha=0.8, adjust_subplots=True, **kwargs):
    ra, dec = ra_dec(evts)
    if ax is None:
        ax = projection_axes(projection=projection)
    ax.plot(ra, dec, marker, markersize=markersize,
            alpha=alpha, **kwargs)
    if adjust_subplots:
        plt.subplots_adjust(top=0.95, bottom=0.0)
    return ax
